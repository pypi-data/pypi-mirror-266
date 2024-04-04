import pandas as pd

def list_flatten(data, fill_value=''):
    # 创建一个 DataFrame
    df = pd.DataFrame({'data': data})
    python
    setup.py
    sdist
    bdist_wheel

    # 定义一个函数来处理每个元素
    def process_item(item):
        if isinstance(item, list) and item:
            return item[0]
        else:
            return fill_value

    # 使用 apply() 方法应用函数到 DataFrame 的每个元素
    df['processed_data'] = df['data'].apply(process_item)

    # 返回处理后的结果
    return df['processed_data'].tolist()


