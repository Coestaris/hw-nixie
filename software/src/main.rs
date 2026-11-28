#![no_std]
#![no_main]

use defmt::export::bool;
use defmt::info;
use embassy_executor::Spawner;
use embassy_time::Timer;
use hw_nixie_fw::bsp::nixie_rev2;
use panic_probe as _;

#[embassy_executor::main]
pub async fn main(_spawner: Spawner) {
    let mut board = nixie_rev2::init();
    info!("Nixie Rev2 initialized!");

    board.set_boost_v(None);

    loop {
        info!("LED On");
        board.set_led(true);
        Timer::after_millis(500).await;

        info!("LED Off");
        board.set_led(false);
        Timer::after_millis(500).await;
    }
}
