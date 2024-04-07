import safetensors as st
from rich.table import Table



def get_tensor_stats(filepath):
    tensor_stats = {}
    with st.safe_open(filepath, "torch") as f:
        for key in f.keys():
            tensor_stats[key] = {
                "shape": f.get_tensor(key).shape,
                "dtype": f.get_tensor(key).dtype,
            }
    return tensor_stats

def tensorstats_to_table(filepath, tensor_stats):
    table = Table(title=f"Tensor Stats <{filepath}>")
    table.add_column("Key")
    table.add_column("Shape")
    table.add_column("Dtype")
    for key in tensor_stats:
        table.add_row(key, str(tensor_stats[key]["shape"]), str(tensor_stats[key]["dtype"]))
    return table