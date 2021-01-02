from flask import Flask,session,current_app
#Principal类似于PyMongo,主要使app有权限的功能
#Permission允许的权限规则
#RoleNeed具体的规则
from flask_principal import Principal,Permission,RoleNeed,identity_changed,Identity,identity_loaded,UserNeed,AnonymousIdentity
app=Flask(__name__)
app.secret_key="secret"
#先用Principal把app包起来
Principal(app)
#建立管理员权限
admin_permission=Permission(RoleNeed("admin"))
#写一信认证方法,把一个用户和admin联系起来
#写一个公共的接收方法,适用于所有的用户
#Principal有一个专门的接收的装饰器 identity_loaded
#接收方法对应了两个参数固定,第一个sender发送者,第二个认证者
@identity_loaded.connect_via(app)
def on_identity_loaded(sender,identity):
    identity.user=session.get("userinfo")
    if session.get("userinfo"):
        identity.provides.add(UserNeed(session.get("userinfo")["name"]))
        identity.provides.add(RoleNeed(session.get("userinfo")["roles"]))

#功能简易化说明:只要地址栏输入/auth,就具备了admin的功能
@app.route("/auth")
def auth():
    #定义了用户,真正开发此功能,可以把用户从数据库中取出,改变其中的某个状态,赋给功能
    #字段中的role表示的是权限,特征就是角色\职位
    userinfo={"name":"lili","roles":"admin"}
    #用户登陆了,必然session中会有数据.flask-principal根据session来工作.
    #把用户的数据写在了session中
    session["userinfo"]=userinfo

        #把当前用户的权限通知给Principal,又由于Principal把app作为参数使用
        #就相当于通知了当前的应用当前用户的状态,这个方法必须要有的通知.
        #identity_changed表示身份的变更,用send方法发送给当前的app
        #flask可以获取当前app,flask里有current_app表示的就是当前app
        #current_app._get_current_object功能是把当前的app作为对象拿出
        #参数identity表示的就是身份
        #下面这句话的功能,就是通知当前app有一种身份用户登录了系统,这种人身份名字是lili
    identity_changed.send(current_app._get_current_object(),identity=Identity(userinfo["name"]))
    #加一个提示信息, 表示执行了这个内容
    return "login"

@app.route("/logout")
def logout():
    session["userinfo"]=""
    identity_changed.send(current_app._get_current_object(), identity=AnonymousIdentity())
    return "logout"
# 把这个权限做为装饰器加到相应的函数上
@app.route("/hello")
@admin_permission.require(401)
def hello():
    return "hello world!"
if __name__=="__main__":
    app.run()