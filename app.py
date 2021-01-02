from flask import Flask,request,render_template
import base64
import face_recognition
from bson.binary import Binary
import pickle
from flask_pymongo import PyMongo
from PIL import Image,ImageDraw
app=Flask(__name__,template_folder="templates",static_folder="static")
#连接mongodb,为app设置的内容
app.config["MONGO_DBNAME"]="myface"
app.config["MONGO_URI"]="mongodb://localhost:27017/myface"
#将app应用与mongodb产生联系,使用PyMongo(app)
mongo=PyMongo(app)
@app.route("/hello",methods=["GET","POST"])
def hello():
    return "hello world"

@app.route("/",methods=["GET","POST"])
def uploadface():
    '''
    功能:接收前端上传来的人脸图片,完成数据库的保存

    1\取上传来的数据的参数 request.form.get("myimg")
    2\上传的数据是base64格式,调用后端的base64进行解码
    3\存到后台变成图片
    4\调用face_reconginition的load_image-file读取文件
    5\调用 face-recognition的face_encodings对脸部进行编码
    6\利用bson和pickle模块组合把脸部编码数据变成128位bitdata数据
    7\利用mongo.db.myface.insert_one插入数据,存储到mongodb里面
    上面是逻辑,但逻辑发生在post方式上,不发生在get,
    限定一下上面逻辑的发生条件,不是POST方式,就是GET,GET请求页面
    :return:
    '''
    if request.method=="POST":
        imgdata=request.form.get("myimg")
        imgdata=base64.b64decode(imgdata)
        with open("a.png","wb") as f:
            f.write(imgdata)
        faceimg=face_recognition.load_image_file("a.png")
        facedata=face_recognition.face_encodings(faceimg)[0]
        print(facedata)
        binary_data = Binary(pickle.dumps(facedata,protocol=-1),subtype=128)
        mongo.db.myface.insert_one({'face':binary_data})

        return {"result":"OK"}
    return render_template("video.html")
@app.route("/check",methods=["GET","POST"])
def checkface():
    '''
        功能:接收前端上传来的人脸图片,完成数据库的保存

        1\取上传来的数据的参数 request.form.get("myimg")
        2\上传的数据是base64格式,调用后端的base64进行解码
        3\存到后台变成图片,取另一个名称
        4\调用face_reconginition的load_image_file读取文件
        5\调用 face-recognition的face_encodings对脸部进行编码
        6\利用pickle模块把脸部的编码从数据库中提取出来
        7\将数据库提取的脸部数据与当前用户在上传的脸部数据进行对比,
        8\如果对比成功,返回ok,如果对比失败,返回:"not you face"
        上面是逻辑,但逻辑发生在post方式上,不发生在get,
        限定一下上面逻辑的发生条件,不是POST方式,就是GET,GET请求页面
        :return:
        '''
    if request.method == "POST":
        imgdata = request.form.get("myimg")
        imgdata = base64.b64decode(imgdata)
        with open("b.png", "wb") as f:
            f.write(imgdata)
        faceimg = face_recognition.load_image_file("b.png")
        facedata = face_recognition.face_encodings(faceimg)[0]
        faces=mongo.db.myface.find()
        for fa in faces:
            #取出的数据是myface数据库中的每一条记录face的"face"键对应的值
            facedata_orign=pickle.loads(fa["face"])
            res=face_recognition.compare_faces([facedata],facedata_orign)
            print(res)
            if res[0]:
                return {"result":"this is true face"}
            else:
                return {"result":"not you face"}
    return render_template("check_face.html")
#把脸部切出来返回前端,前端显示切出来的脸部
@app.route("/cut",methods=["GET","POST"])
def cutface():
    '''
           功能:接收前端上传来的人脸图片,完成数据库的保存

           1\取上传来的数据的参数 request.form.get("myimg")
           2\上传的数据是base64格式,调用后端的base64进行解码
           3\存到后台变成图片,取另一个名称
           4\调用face_reconginition的load_image_file读取文件
           5\调用 face-recognition的face_locations输出脸部的坐标
           6\利用坐标的索引值把图片数据做切片
           7\保存一下切片后的数据
           8\切片后的数据能不能用bae64的编码返回前端
           9\前端显示切片后的数据
           上面是逻辑,但逻辑发生在post方式上,不发生在get,
           限定一下上面逻辑的发生条件,不是POST方式,就是GET,GET请求页面
           :return:
           '''
    if request.method == "POST":
        imgdata = request.form.get("myimg")
        imgdata = base64.b64decode(imgdata)
        with open("c.png", "wb") as f:
            f.write(imgdata)
        faceimg = face_recognition.load_image_file("c.png")
        locations=face_recognition.face_locations(faceimg)
        print(locations)
        for location in locations:
            top,right,bottom,left=location
            #按行列来做切片
            image = Image.fromarray(sub_face)
            image.save("d.png")
            sub_face=faceimg[top:bottom,left:right]

        #无论图片怎么存,都在转成base64编码,前端能够接收的图片代码永远都是base64
        with open("d.png","rb")  as f:
            imgcode=base64.b64encode(f.read())
        #base64.b64encode可以转码
        print(imgcode)
        return {"result":imgcode.decode("utf8")}
        #with open('d.png',"wb") as f:
        #f.write(sub_face)
        #imgdata=base64.b64encode(sub_face)
        #return {"result":imgdata}
    return render_template("cut_face.html")
@app.route("/hua",methods=["POST","GET"])
def hua():
    '''
               功能:接收前端上传来的人脸图片,完成数据库的保存

               1\取上传来的数据的参数 request.form.get("myimg")
               2\上传的数据是base64格式,调用后端的base64进行解码
               3\存到后台变成图片,取另一个名称
               4\调用face_reconginition的load_image_file读取文件
               5\调用 face-recognition的face_landmarks输出脸部的五官
               6\对五官进行图片的修饰(画多边形,线)
               7\保存一下图片
               8\用bae64的编码返回前端
               9\前端显示化妆后的数据
               上面是逻辑,但逻辑发生在post方式上,不发生在get,
               限定一下上面逻辑的发生条件,不是POST方式,就是GET,GET请求页面
               :return:
               '''
    if request.method == "POST":
        imgdata = request.form.get("myimg")
        imgdata = base64.b64decode(imgdata)
        with open("e.png", "wb") as f:
            f.write(imgdata)
        faceimg = face_recognition.load_image_file("e.png")
        landmarks=face_recognition.face_landmarks(faceimg)
        print(landmarks)
        #利用landmarks里面的各个键的特征,来画内容,画内容形成图片
        #通过Pillow中Image模块进行画图
        image=Image.fromarray(faceimg)
        draw=ImageDraw.Draw(image)
        for landmark in landmarks:
            #pylygon指的是画多边形,画的眼眉
            draw.polygon(landmark["left_eyebrow"],fill=(68,54,50,128))
            draw.polygon(landmark["right_eyebrow"],fill=(68,54,50,128))
            draw.line(landmark["left_eye"],fill=(0,0,0,110),width=2)
            draw.line(landmark["right_eye"],fill=(0,0,0,110),width=2)
            draw.polygon(landmark["nose_bridge"],fill=(204,73,45,150))
            draw.polygon(landmark["top_lip"],fill=(150,0,0,128))
            draw.polygon(landmark["bottom_lip"],fill=(150,0,0,128))
        image.save("f.png")
        with open("f.png","rb") as f:
            huapic=base64.b64encode(f.read())
        return {"result":huapic.decode("utf8")}
    return render_template("hua_face.html")

if __name__=="__main__":
    app.run()