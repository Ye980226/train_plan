
import shutil
import pandas as pd
import json
import re
import os
import matplotlib
import matplotlib.pyplot as plt
import glob
from io import BytesIO
import base64
from PIL import Image
from flask import Flask, request, make_response, render_template, redirect, url_for
from werkzeug.utils import secure_filename  # 使用这个是为了确保filename是安全的
app = Flask(__name__)

plt.switch_backend('agg')
SRC = "src"
myfont = matplotlib.font_manager.FontProperties(fname="simhei.ttf")
plt.rcParams['axes.unicode_minus'] = False  # 解决保存图像是负号'-'显示为方块的问题
df_dict = {}


@app.route('/')
def hello():
    df = pd.read_excel("./static/uploads/train.xlsx")

    df = df.dropna()
    df = df.applymap(lambda x: json.loads(x))
    columns = re.search(r"(\[.*?\])", df.columns[0]).group(1)
    species = columns.replace("[", "").replace("]", "").split(",")
    length = len(species)
    if os.path.exists(SRC):

        shutil.rmtree(SRC)
    for i in range(length):
        df_dict[species[i]] = df.applymap(lambda x: x[i])
        df_dict[species[i]].columns = list(
            map(lambda x: x.replace(columns, species[i]), df_dict[species[i]].columns))

        if not os.path.exists(SRC):

            os.mkdir(SRC)
        for index in set(df_dict[species[i]].index):
            df_dict[species[i]].loc[index].plot(
                figsize=(15, 7))
            plt.legend(df_dict[species[i]].loc[index].columns,
                       prop=myfont)
            plt.title(index+"_"+species[i], fontproperties=myfont)
            plt.savefig(os.path.join(SRC, index+"_"+species[i]+".jpg"))

    files = glob.glob("./src/*")
    # width = 2
    length = len(files)
    ims = [Image.open(file) for file in files]
    width, height = ims[0].size
    result = Image.new(ims[0].mode, (width, height * length))
    for i,im in enumerate(ims):
        result.paste(im, box=(0, i * height))
    
    # plt.figure(figsize=(15, 7*length), dpi=2**7)
    # for i in range(len(files)):
        # ax = plt.subplot(length, 1, i+1)

        # plt.title(files[i].replace(
            # "./src\\", " ").replace(".jpg", ""), fontproperties=myfont)

        # plt.imshow(Image.open(files[i]))
    # plt.subplots_adjust(bottom=0.2,
                        # top=0.8)
    result.save("output.png")
    with open("output.png", "rb") as f:
        # b64encode是编码，b64decode是解码
        data = base64.b64encode(f.read()).decode()
        # base64.b64decode(base64data)
        print(data)

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
    app.run(host="0.0.0.0", port=9999, debug=True)
