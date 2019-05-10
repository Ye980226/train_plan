
import pandas as pd
import json
import re
import os
import matplotlib.pyplot as plt
import glob
from io import BytesIO
import base64
from PIL import Image
from flask import Flask, request, make_response, render_template, redirect, url_for
from werkzeug.utils import secure_filename  # 使用这个是为了确保filename是安全的
app = Flask(__name__)


SRC = "src"
plt.rcParams['font.sans-serif'] = ['FangSong']  # 指定默认字体
plt.rcParams['axes.unicode_minus'] = False  # 解决保存图像是负号'-'显示为方块的问题
df_dict = {}


@app.route('/')
def hello():
    df = pd.read_excel("train.xlsx")

    df = df.dropna()
    df = df.applymap(lambda x: json.loads(x))
    columns = re.search(r"(\[.*?\])", df.columns[0]).group(1)
    species = columns.replace("[", "").replace("]", "").split(",")
    length = len(species)

    for i in range(length):
        df_dict[species[i]] = df.applymap(lambda x: x[i])
        df_dict[species[i]].columns = list(
            map(lambda x: x.replace(columns, species[i]), df_dict[species[i]].columns))

        if not os.path.exists(SRC):

            os.mkdir(SRC)
        for index in set(df_dict[species[i]].index):
            df_dict[species[i]].loc[index].plot(figsize=(15, 7))
            plt.savefig(os.path.join(SRC, index+"_"+species[i]+".jpg"))

    context = {}

    files = glob.glob("./src/*")
    # width = 2
    length = len(files)
    plt.figure(figsize=(15, 7*length), dpi=2**8)
    for i in range(len(files)):
        ax = plt.subplot(length, 1, i+1)

        plt.title(files[i].replace(
            "./src\\", " ").replace(".jpg", ""))

        plt.imshow(Image.open(files[i]))
    plt.subplots_adjust(bottom=0.2,
                        top=0.8)

    sio = BytesIO()
    plt.savefig(sio, format='png')
    data = base64.encodebytes(sio.getvalue()).decode()

    html = '''
       <html>
           <body>
               <img src="data:image/png;base64,{}" />
           </body>
        <html>
    '''
    plt.close()
    return html.format(data)


@app.route("/upload", methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        f = request.files["file"]
        base_path = os.path.abspath(os.path.dirname(__file__))
        upload_path = os.path.join(base_path, "static/uploads")
        file_name = upload_path + "/" + secure_filename(f.filename)

        f.save(file_name)
        return redirect(url_for('upload'))
    return render_template('upload.html')


def show():
    pd.Panel(df_dict).to_excel("output.xlsx")
    return "ok"


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=9999)
