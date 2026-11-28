//! Board support for the STM32U073-based Nixie Rev2 motherboard.

use core::cell::RefCell;

use critical_section::{Mutex, RestoreState};
use embassy_stm32::{
    dac::{DacChannel, Value},
    gpio::{Input, Level, Output, Pull, Speed},
    mode::Blocking,
    usart::{Config as UartConfig, UartTx},
};

pub use crate::{
    button::Button,
    tube::{Cathode, Tube},
};

#[defmt::global_logger]
struct UartLogger;

struct LoggerState {
    uart: Option<UartTx<'static, Blocking>>,
    encoder: defmt::Encoder,
    restore: Option<RestoreState>,
}

static LOGGER: Mutex<RefCell<LoggerState>> = Mutex::new(RefCell::new(LoggerState {
    uart: None,
    encoder: defmt::Encoder::new(),
    restore: None,
}));

pub struct Board {
    led: Output<'static>,
    buttons: [Input<'static>; 3],
    anodes: [Output<'static>; 4],
    cathode_data: Output<'static>,
    cathode_clock: Output<'static>,
    cathode_latch: Output<'static>,
    cathode_state: u16,
    boost_enable: Output<'static>,
    boost_control: DacChannel<'static, Blocking>,
}

/// Initialize the board with the LED, tube drivers, and boost converter off.
/// Call once at startup.
pub fn init() -> Board {
    let p = embassy_stm32::init(Default::default());
    let boost_enable = Output::new(p.PA3, Level::Low, Speed::Low);
    let anodes = [
        Output::new(p.PA15, Level::Low, Speed::Low),
        Output::new(p.PB3, Level::Low, Speed::Low),
        Output::new(p.PB4, Level::Low, Speed::Low),
        Output::new(p.PB5, Level::Low, Speed::Low),
    ];
    let mut uart_config = UartConfig::default();
    uart_config.baudrate = 115_200;
    // USART1_TX on PA9 reaches pin 1 of J2 through R61.
    let log_uart =
        UartTx::new_blocking(p.USART1, p.PA9, uart_config).expect("Rev2 log UART configuration");

    critical_section::with(|cs| LOGGER.borrow_ref_mut(cs).uart = Some(log_uart));

    let mut board = Board {
        led: Output::new(p.PA8, Level::Low, Speed::Low),
        buttons: [
            Input::new(p.PA7, Pull::None),
            Input::new(p.PA5, Pull::None),
            Input::new(p.PA6, Pull::None),
        ],
        anodes,
        cathode_data: Output::new(p.PB15, Level::Low, Speed::Low),
        cathode_clock: Output::new(p.PB13, Level::Low, Speed::Low),
        cathode_latch: Output::new(p.PB12, Level::Low, Speed::Low),
        cathode_state: 0,
        boost_enable,
        boost_control: DacChannel::new_blocking(p.DAC1, p.PA4),
    };
    board.clear_cathodes();
    board
}

impl Board {
    pub fn set_led(&mut self, enabled: bool) {
        self.led.set_level(enabled.into());
    }

    /// Read the current button state. The board has external pull-downs.
    pub fn read_button(&self, button: Button) -> bool {
        let index = match button {
            Button::Plus => 0,
            Button::Minus => 1,
            Button::Set => 2,
        };
        self.buttons[index].is_high()
    }

    pub fn set_anode(&mut self, tube: Tube, enabled: bool) {
        let index = match tube {
            Tube::N1 => 0,
            Tube::N2 => 1,
            Tube::N3 => 2,
            Tube::N4 => 3,
        };
        self.anodes[index].set_level(enabled.into());
    }

    /// Set a cathode on the shared bus, preserving the other cathode states.
    pub fn set_cathode(&mut self, cathode: Cathode, enabled: bool) {
        let mask = cathode_mask(cathode);
        if enabled {
            self.cathode_state |= mask;
        } else {
            self.cathode_state &= !mask;
        }
        self.write_cathodes();
    }

    pub fn clear_cathodes(&mut self) {
        self.cathode_state = 0;
        self.write_cathodes();
    }

    /// Set the nominal boost output in whole volts, clamping requests to 120–180 V.
    ///
    /// The Rev2 feedback network has a nominal floor of 128.8 V at DAC code zero.
    /// Requests below that floor use code zero. The output depends on the actual
    /// reference voltage, component tolerances, and load.
    pub fn set_boost_v(&mut self, volts: Option<u16>) {
        self.set_boost(volts.map(|volts| {
            const FEEDBACK_V: f32 = 1.25;
            const UPPER_FEEDBACK_OHMS: f32 = 3_000_000.0; // R10 + R11 + R12
            const LOWER_FEEDBACK_OHMS: f32 = 29_400.0; // R13
            const CONTROL_DIVIDER: f32 = 5_100.0 / (62_000.0 + 5_100.0); // R4 / (R3 + R4)
            const SENSE_OHMS: f32 = 14_700.0; // R7
            const DAC_REFERENCE_V: f32 = 3.3;
            const DAC_MAX_CODE: f32 = 4095.0;

            // Q1 sinks the current set by the divided DAC voltage and R7 from FB.
            let output_floor = FEEDBACK_V * (1.0 + UPPER_FEEDBACK_OHMS / LOWER_FEEDBACK_OHMS);
            let control_gain = UPPER_FEEDBACK_OHMS * CONTROL_DIVIDER / SENSE_OHMS;
            let control_v = (f32::from(volts.clamp(128, 160)) - output_floor) / control_gain;
            (control_v.clamp(0.0, DAC_REFERENCE_V) * DAC_MAX_CODE / DAC_REFERENCE_V + 0.5) as u16
        }));
    }

    /// Enable or adjust the boost converter with a raw 12-bit DAC code.
    /// The code controls the feedback circuit. Pass `None` to disable the converter.
    pub fn set_boost(&mut self, control_code: Option<u16>) {
        if let Some(code) = control_code {
            self.boost_control.set(Value::Bit12Right(code.min(4095)));
            self.boost_enable.set_high();
        } else {
            self.boost_enable.set_low();
        }
    }

    fn write_cathodes(&mut self) {
        // Shift the high byte through U13 into U12, then latch both registers.
        self.cathode_latch.set_low();
        for bit in (0..16).rev() {
            self.cathode_data
                .set_level((self.cathode_state & (1 << bit) != 0).into());
            self.cathode_clock.set_high();
            self.cathode_clock.set_low();
        }
        self.cathode_latch.set_high();
        self.cathode_latch.set_low();
    }
}

fn cathode_mask(cathode: Cathode) -> u16 {
    // U13 receives the low byte and U12 receives the high byte.
    // In each byte, QA is bit 0 and QH is bit 7.
    let bit = match cathode {
        Cathode::Zero => 2,
        Cathode::One => 4,
        Cathode::Two => 5,
        Cathode::Three => 3,
        Cathode::Four => 1,
        Cathode::Five => 13,
        Cathode::Six => 11,
        Cathode::Seven => 9,
        Cathode::Eight => 10,
        Cathode::Nine => 12,
        Cathode::DecimalPoint => 14,
    };
    1 << bit
}

impl LoggerState {
    fn encode(&mut self, encode: impl FnOnce(&mut defmt::Encoder, &mut dyn FnMut(&[u8]))) {
        if let Some(uart) = &mut self.uart {
            encode(&mut self.encoder, &mut |bytes| {
                let _ = uart.blocking_write(bytes);
            });
        }
    }
}

// Keep interrupts masked across each frame to prevent interleaving.
unsafe impl defmt::Logger for UartLogger {
    fn acquire() {
        // SAFETY: release() restores this exact critical-section state.
        let restore = unsafe { critical_section::acquire() };
        critical_section::with(|cs| {
            let mut state = LOGGER.borrow_ref_mut(cs);
            assert!(state.restore.is_none(), "reentrant defmt logging");
            state.restore = Some(restore);
            state.encode(|encoder, emit| encoder.start_frame(emit));
        });
    }

    unsafe fn write(bytes: &[u8]) {
        critical_section::with(|cs| {
            LOGGER
                .borrow_ref_mut(cs)
                .encode(|encoder, emit| encoder.write(bytes, emit));
        });
    }

    unsafe fn flush() {
        critical_section::with(|cs| {
            if let Some(uart) = &mut LOGGER.borrow_ref_mut(cs).uart {
                let _ = uart.blocking_flush();
            }
        });
    }

    unsafe fn release() {
        let restore = critical_section::with(|cs| {
            let mut state = LOGGER.borrow_ref_mut(cs);
            state.encode(|encoder, emit| encoder.end_frame(emit));
            state.restore.take().expect("defmt logger is acquired")
        });
        // SAFETY: This matches the acquisition in acquire().
        unsafe { critical_section::release(restore) };
    }
}
