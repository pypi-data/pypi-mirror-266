use hex_renderer::options::{OverloadOptions, Color, Marker};
use interface_macros::py_gen;
use pyo3::{Python, types::PyModule, PyResult};

use super::{color::PyColor, marker::PyMarker};

pub fn add_class(py: Python, m: &PyModule) -> PyResult<()> {
    let sub_m = PyModule::new(py, "OverloadOptions")?;
    sub_m.add_class::<PyOverloadOptionsDashes>()?;
    sub_m.add_class::<PyOverloadOptionsLabeledDashes>()?;
    sub_m.add_class::<PyOverloadOptionsMatchedDashes>()?;
    
    m.add_submodule(sub_m)?;

    Ok(())
}

#[py_gen(bridge = OverloadOptions)]
#[derive(Clone)]
///Options for what to do when you get too many parallel lines
pub enum PyOverloadOptions {
    #[derive(Clone, PartialEq, PartialOrd, Debug)]
    ///same as CollisionOption.Dashes (just draws dashes of the given color over the first line)
    Dashes(
        #[py_gen(name = "color", bridge = PyColor)]
        Color
    ),
    #[derive(Clone, PartialEq, PartialOrd, Debug)]
    ///Similar to OverloadOptions.Dashes except it includes a label with the number of overlapping lines
    LabeledDashes {
        #[py_gen(bridge = PyColor)]
        ///Color to draw the dashes with
        color: Color,
        #[py_gen(bridge = PyMarker)]
        ///marker for size and color to draw the label
        label: Marker
    },
    #[derive(Clone, PartialEq, PartialOrd, Debug)]
    ///same as CollisionOption,MatchedDashes (represents them as dashes that represet each color of overlapping lines)
    MatchedDashes
}