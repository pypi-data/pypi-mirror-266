import scanpy as sc
print("read_10x")
adata = sc.read_10x_mtx(
                '../data/0_RNA',# the directory with the `.mtx` file
                var_names='gene_symbols',                # use gene symbols for the variable names (variables-axis index)
                cache=True)
print(adata)