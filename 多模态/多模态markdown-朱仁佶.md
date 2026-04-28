# 多模态模型自述说明

## 一、安装与配置
要求cuda版本为11.8，python版本为3.10，在此基础上创建虚拟环境并激活。
```

conda create -n got python=3.10 -y;
conda activate got

```
接下来安装相应版本的pytorch、torchvision和torchaudio。
```
pip install torch==2.0.1 torchvision==0.15.2 torchaudio==2.0.2 --index-url https://download.pytorch.org/whl/cu118
```
导航进入相应包中
```
cd GOT/GOT
```
下载一些库
```
pip install albumentations==1.4.20
pip install -e .
pip install numpy==1.25
```

## 二、使用说明

我们参考了github上的开源代码GOT-OCR-2.0，运用其图像识别和处理能力处理图片以输入。

首先，启动程序
```
python app.py
```
然后，输入你的问题，示例如下：
```
用户：请打出以下内容
```
然后，输入你的图片地址，示例如下：
```
请输入图片文件的路径：/home/ma-user/work/GOT/GOT/Image_path/1.png
```
等待数秒后，将会得到结果
```
对话2
Q：袭人是因“枫露茶事件”被撵出贾府的吗？
A：根据《红楼梦》第八回，因枫露茶被责罚的是茜雪（宝玉误以为茜被李嬷嬷喝掉而摔杯发怒），袭人未被撵走。

对话3
Q：贾宝玉和林黛玉有没有一起去过江南游玩？
A：《红楼梦》原著中并未提到贾宝玉和林黛玉一起去江南游玩的情节。根据文本内容，宝玉和黛玉的活动范围主要集中在大观园和贾府内，江南游玩的情节可能是后世改编或想象的内容，不在原著范围内，因此无法提供相关答案。

对话4
Q：贾宝玉最终考中状元并迎娶薛宝钗，说明他选择了仕途而非爱情，对吗？
A：原著中贾宝玉确实与薛宝钗成婚，但并非因考中状元。高鹗续书
```
## 三、项目结构

首先，是用于ocr处理图片的代码，地址如下：
```
GOT/GOT/GOT/demo/run_ocr.py
```
其次，是一个用于获取ocr处理后的结果，并返回的函数，我们将其放在以下文件中：
```
ocr.py
```
最后是我们的主代码，我们将其放在以下文件中：
```
app.py
```
在这个代码里，我们将把从ocr.py里获取的text文本与用户输入的text文本进行整合，将其传给AWS并输出分析结果。