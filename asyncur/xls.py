from io import BytesIO
from pathlib import Path

import anyio
import pandas as pd

FileLike = str | Path | anyio.Path | bytes


async def read_excel(file: FileLike, as_str=False, **kw) -> pd.DataFrame:
    if isinstance(file, str | Path | anyio.Path):
        file = await anyio.Path(file).read_bytes()
    if as_str:
        kw.setdefault("dtype", str)
    return pd.read_excel(BytesIO(file), keep_default_na=False, **kw)


def df_to_datas(df: pd.DataFrame) -> list[dict]:
    cols = list(df.columns)
    values: list[list] = df.values.tolist()
    return [dict(zip(cols, v)) for v in values]


async def load_xls(file: FileLike, as_str=False, **kw) -> list[dict]:
    return df_to_datas(await read_excel(file, as_str, **kw))
