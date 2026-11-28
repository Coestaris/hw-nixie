/// One of the four tube positions in the clock display.
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum Tube {
    N1,
    N2,
    N3,
    N4,
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
/// A digit or decimal point on a Nixie tube.
pub enum Cathode {
    Zero,
    One,
    Two,
    Three,
    Four,
    Five,
    Six,
    Seven,
    Eight,
    Nine,
    DecimalPoint,
}
