from typing import Dict, List, Tuple, Any
import h5py
import numpy as np

from hw2d.utils.namespaces import Namespace


def get_save_params(
    params: Dict[str, Any], dt: float, snaps: int, x: int, y: int, x_save: int or None = None, y_save: int or None = None
) -> Dict[str, Any]:
    params = params.copy()
    params["dt"] = dt
    params["frame_dt"] = dt * snaps
    params["x"] = x
    params["y"] = y
    params["x_save"] = x_save if x_save is not None else x
    params["y_save"] = y_save if y_save is not None else y
    params["grid_pts"] = x
    return params


def create_appendable_h5(
    filepath: str,
    params: Dict[str, Any],
    dtype: np.dtype = np.float32,
    chunk_size: int = 100,
    field_list: List[str] = ["density", "omega", "phi"],
    properties: List[str] = [],
    add_last_state: bool = True,
) -> None:
    y_save = params["y_save"]
    x_save = params["x_save"]
    with h5py.File(f"{filepath}", "w") as hf:
        # Add simulation fields
        for field_name in field_list:
            hf.create_dataset(
                field_name,
                dtype=dtype,
                shape=(0, y_save, x_save),
                maxshape=(None, y_save, x_save),
                chunks=(chunk_size, y_save, x_save),
                compression="gzip",
            )
        # Add properties
        for prop_name in properties:
            hf.create_dataset(
                prop_name,
                dtype=dtype,
                shape=(0, 1),
                maxshape=(None, 1),
                chunks=(chunk_size, 1),
                compression="gzip",
            )
        # Add last state for continuation
        if add_last_state:
            for field_name in ["density", "phi", "omega"]:
                hf.create_dataset(f"state_{field_name}", (params["y"], params["x"]), dtype=np.float64)
        # Add simulation parameters
        for key, value in params.items():
            hf.attrs[key] = value
    print(f"Created: {filepath}")


def append_h5(output_path: str, buffer: np.ndarray, buffer_index: int) -> None:
    """append a file, from buffer, with buffer_index size"""
    with h5py.File(output_path, "a") as hf:
        for field_name in buffer.keys():
            _ = hf[field_name].resize((hf[field_name].shape[0] + buffer_index), axis=0)
            hf[field_name][-buffer_index:] = buffer[field_name][:buffer_index]


def update_last_state(output_path: str, last_state: Dict[str, Any]) -> None:
    with h5py.File(output_path, "r+") as hf:
        for name, value in last_state.items():
            hf[name][:] = value


def save_to_buffered_h5(
    buffer: Dict[str, Any],
    buffer_length: int,
    buffer_index: int,
    new_val: Dict[str, Any],
    output_path: str,
    last_state: Dict[str, Any] = {}
) -> int:
    """
    Save data to a buffer. If the buffer is full, flush the buffer to the HDF5 file.

    Args:
        buffer (Dict[str, Any]): Data buffer.
        buffer_length (int): Maximum size of the buffer.
        new_val (Dict[str, Any]): New values to be added to the buffer.
        field_list (List[str]): List of fields to be saved.
        buffer_index (int): Current index in the buffer.
        flush_index (int): Index to start flushing in the HDF5 file.
        output_path (str): Path of the output HDF5 file.

    Returns:
        Tuple[int, int]: Updated buffer index and flush index.
    """
    for idx, field in enumerate(buffer.keys()):
        buffer[field][buffer_index] = new_val[field]
    buffer_index += 1
    # If buffer is full, flush to HDF5 and reset buffer index
    if buffer_index == buffer_length:
        append_h5(output_path, buffer, buffer_index)
        if last_state:
            update_last_state(output_path, last_state)
        buffer_index = 0
    return buffer_index


def create_fixed_h5(
    file_path: str,
    time: int,
    y: int,
    x: int,
    chunk_size: int = 100,
    compression: str = "gzip",
    field_list: List = ["density", "omega", "phi"],
    dtype=np.float32,
) -> None:
    with h5py.File(file_path, "w") as hf:
        for field_name in field_list:
            hf.create_dataset(
                field_name,
                dtype=dtype,
                shape=(time, y, x),
                maxshape=(None, y, x),
                chunks=(chunk_size, y, x),
                compression=compression,
            )


def load_h5_data(
    file_name: str, field_list: List[str]
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Load data and attributes from an HDF5 file.

    Args:
        file_name (str): Name and path of the HDF5 file to load.
        field_list (List[str]): List of fields to be loaded.

    Returns:
        Tuple[Dict[str, Any], Dict[str, Any]]: Loaded data and associated parameters (attributes).
    """
    with h5py.File(file_name, "r") as h5_file:
        data = {}
        for field in field_list:
            data[field] = h5_file[field][:]
        params = dict(h5_file.attrs)
    return data, params


def continue_h5_file(
    file_name: str, field_list: List[str]
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Load data and attributes from an HDF5 file.

    Args:
        file_name (str): Name and path of the HDF5 file to load.
        field_list (List[str]): List of fields to be loaded.

    Returns:
        Tuple[Dict[str, Any], Dict[str, Any]]: Loaded data and associated parameters (attributes).
    """
    lengths = []
    with h5py.File(file_name, "r") as h5_file:
        # properties
        attributes = dict(h5_file.attrs)
        data = {}
        for field in field_list:
            # Load saved state
            if f"state_{field}" in h5_file.keys():
                data[field] = h5_file[f"state_{field}"][:].astype(np.float64)
            else:
                data[field] = h5_file[field][-1].astype(np.float64)
            # Load Length
            lengths.append(len(h5_file[field]))
        # Age
        age = h5_file["time"][-1][0]
        #age = params["frame_dt"] * (length - 1)
    length = min(lengths)
    # Prepare data structure
    data = Namespace(**data, age=age)
    physics_params = {
        k: attributes[k]
        for k in ("dx", "N", "c1", "nu", "k0", "poisson_bracket_coeff", "kappa_coeff")
    }
    return data, physics_params
