use hex_renderer::options::{Color, OverloadOptions, CollisionOption};
use interface_macros::py_gen;
use pyo3::{Python, types::PyModule, PyResult};

use super::{color::PyColor, overload_options::PyOverloadOptions};

pub fn add_class(py: Python, m: &PyModule) -> PyResult<()> {
    let sub_m = PyModule::new(py, "CollisionOption")?;
    sub_m.add_class::<PyCollisionOptionDashes>()?;
    sub_m.add_class::<PyCollisionOptionMatchedDashes>()?;
    sub_m.add_class::<PyCollisionOptionParallelLines>()?;
    sub_m.add_class::<PyCollisionOptionOverloadedParallel>()?;
    
    m.add_submodule(sub_m)?;

    Ok(())
}

#[py_gen(bridge = CollisionOption)]
#[derive(Clone)]
#[derive(Debug, Clone, Copy)]
///Options for drawing overlapping segments (impossible patterns)
pub enum PyCollisionOption {
    #[derive(Clone, PartialEq, PartialOrd, Debug)]
    ///Draws the first segment and then dashes of the given color for the rest
    Dashes(
        #[py_gen(name = "color", bridge = PyColor)]
        ///Color of dashes to draw with
        Color
    ),
    #[derive(Clone, PartialEq, PartialOrd, Debug)]
    ///Draws the line as a set of dashes where the dash marks match the colors of the overlapping lines
    MatchedDashes,
    #[derive(Clone, PartialEq, PartialOrd, Debug)]
    ///Draws each of the segments as smaller, parallel lines all next to eachother
    ParallelLines,
    #[derive(Clone, PartialEq, PartialOrd, Debug)]
    ///Same as CollisionOption.ParallelLines except with an escape when you get too many overlaps
    OverloadedParallel {
        ///number of overlapping segments/lines before using the overload option
        max_line: usize,
        #[py_gen(bridge = PyOverloadOptions)]
        ///Rendering option for when reaching too many parallel lines
        overload: OverloadOptions
    }
}