use hex_renderer::options::{Point, Marker};
use interface_macros::py_gen;
use pyo3::{Python, types::PyModule, PyResult};

use super::marker::PyMarker;

pub fn add_class(py: Python, m: &PyModule) -> PyResult<()> {
    let sub_m = PyModule::new(py, "Point")?;
    sub_m.add_class::<PyPointNone>()?;
    sub_m.add_class::<PyPointSingle>()?;
    sub_m.add_class::<PyPointDouble>()?;
    
    m.add_submodule(sub_m)?;

    Ok(())
}

#[py_gen(bridge = Point)]
#[derive(Clone)]
///Options for drawing points at the grid points/intersections
pub enum PyPoint {
    #[derive(Clone, PartialEq, PartialOrd, Debug)]
    ///Doesn't draw any points
    None,
    #[derive(Clone, PartialEq, PartialOrd, Debug)]
    ///Draws a single dot
    Single(
        #[py_gen(name = "marker", bridge = PyMarker)]
        ///Marker specifying radius and color of point
        Marker
    ),
    #[derive(Clone, PartialEq, PartialOrd, Debug)]
    ///Draws an inner dot dotand outer dot (or a point with a border)
    Double { 
        #[py_gen(bridge = PyMarker)]
        ///Marker specifying radius and color of the inner point
        inner: Marker,
        #[py_gen(bridge = PyMarker)]
        ///Marker specifying radius and color of the outer point
        outer: Marker 
    },
}