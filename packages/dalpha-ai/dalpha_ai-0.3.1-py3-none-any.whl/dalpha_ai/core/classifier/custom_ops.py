import onnxscript
import torch

# Assuming you use opset18
from onnxscript.onnx_opset import opset17 as op

custom_opset = onnxscript.values.Opset(domain="onnx-script", version=17)


@onnxscript.script(custom_opset)
def ScaledDotProductAttention(
    query,
    key,
    value,
    dropout_p,
):
    # Swap the last two axes of key
    key_shape = op.Shape(key)
    key_last_dim = key_shape[-1:]
    key_second_last_dim = key_shape[-2:-1]
    key_first_dims = key_shape[:-2]
    # Contract the dimensions that are not the last two so we can transpose
    # with a static permutation.
    key_squeezed_shape = op.Concat(
        op.Constant(value_ints=[-1]), key_second_last_dim, key_last_dim, axis=0
    )
    key_squeezed = op.Reshape(key, key_squeezed_shape)
    key_squeezed_transposed = op.Transpose(key_squeezed, perm=[0, 2, 1])
    key_transposed_shape = op.Concat(
        key_first_dims, key_last_dim, key_second_last_dim, axis=0
    )
    key_transposed = op.Reshape(key_squeezed_transposed, key_transposed_shape)

    embedding_size = op.CastLike(op.Shape(query)[-1], query)
    scale = op.Div(1.0, op.Sqrt(embedding_size))

    # Scale q, k before matmul for stability see https://tinyurl.com/sudb9s96 for math
    query_scaled = op.Mul(query, op.Sqrt(scale))
    key_transposed_scaled = op.Mul(key_transposed, op.Sqrt(scale))
    attn_weight = op.Softmax(
        op.MatMul(query_scaled, key_transposed_scaled),
        axis=-1,
    )
    attn_weight, _ = op.Dropout(attn_weight, dropout_p)
    return op.MatMul(attn_weight, value)


# ScaledDotProductAttention.opname = ScaledDotProductAttention.name


def custom_scaled_dot_product_attention(
    g, query, key, value, attn_mask, dropout, is_causal, scale=None
):
    return g.onnxscript_op(
        ScaledDotProductAttention, query, key, value, dropout
    ).setType(query.type())
