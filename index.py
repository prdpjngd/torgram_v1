import aria2p
import subprocess
from flask import Flask, render_template, request, redirect, make_response, session,url_for,send_from_directory
app = Flask(__name__)

#how to get environment varible values -->  " os.environ['S3_KEY'] "
aria2 = aria2p.API(
        aria2p.Client(
            host="http://localhost",
            port=6800,
            secret=""
        )
    )

@app.route('/run',methods = ['GET'])
def run():
    aria2_daemon_start_cmd = []
    aria2_daemon_start_cmd.append("aria2c")
    aria2_daemon_start_cmd.append("--daemon=true")
    aria2_daemon_start_cmd.append("--enable-rpc")
    aria2_daemon_start_cmd.append("--follow-torrent=mem")
    aria2_daemon_start_cmd.append("--max-connection-per-server=10")
    aria2_daemon_start_cmd.append("--min-split-size=10M")
    aria2_daemon_start_cmd.append("--rpc-listen-all=false")
    aria2_daemon_start_cmd.append("--rpc-listen-port=6800")
    aria2_daemon_start_cmd.append("--rpc-max-request-size=1024M")
    aria2_daemon_start_cmd.append("--seed-ratio=0.0")
    aria2_daemon_start_cmd.append("--seed-time=1")
    aria2_daemon_start_cmd.append("--split=10")
    aria2_daemon_start_cmd.append("--bt-stop-timeout=600")
    aria2_daemon_start_cmd.append("--dir=/app/static/files")
    #aria2_daemon_start_cmd.append("--dir=/Users/pradeepjangid/torgram/static/files")
    subprocess.Popen(aria2_daemon_start_cmd)
    subprocess.call

    #downloads = aria2.get_downloads()
    #list1=[]
    #for download in downloads:
        #list1.append(download.name)
        #list1.append(download.download_speed)
        #list1.append("<br>")
    return 'TRUE'

@app.route('/',methods = ['GET'])
def home():
    downloads = aria2.get_downloads()
    opt=[]
    for download in downloads:
        tmp=[]
        tmp.append(str(download.name))
        tmp.append(str(download.download_speed_string()))
        tmp.append(str(download.total_length_string()))
        tmp.append(str(download.connections))
        tmp.append(str(download.progress_string()))
        if str(download.status)=='active':
            tmp.append('bg-success progress-bar-striped progress-bar-animated')
        elif str(download.status)=='complete':
            tmp.append('progress-bar-info')
        else:
            tmp.append('bg-danger progress-bar-striped')
        tmp.append(str(download.eta_string()))
        tmp.append(str(download.gid))
        opt.append(tmp)
    return render_template('index.html',opt=opt)

@app.route('/home',methods = ['GET'])
def list():
    # list downloads
    downloads = aria2.get_downloads()
    opt=''
    for download in downloads:
        opt=opt+'Name : '+str(download.name)+'<br>'
        opt=opt+'D Speed : '+str(download.download_speed_string())+'<br>'
        opt=opt+'Total : '+str(download.total_length_string())+'<br>'
        opt=opt+'Seeds and peers  : '+str(download.connections)+'<br>'
        opt=opt+'Progress : '+str(download.progress_string())+'<br>'
        opt=opt+'status : '+str(download.status)+'<br>'
        opt=opt+'ETA : '+str(download.eta_string())+'<br><hr>'
    return str(opt)


@app.route('/pause',methods = ['GET'])
def pause():
    gid = request.args.get('gid')
    tmp = aria2.get_download(gid)
    if tmp.status=='paused':
        return 'False'
    else:
        tmp.pause()
        return 'True'

@app.route('/resume',methods = ['GET'])
def resume():
    gid = request.args.get('gid')
    tmp = aria2.get_download(gid)
    if tmp.status=='active':
        return 'False'
    else:
        tmp.resume()
        return 'True'

@app.route('/stop',methods = ['GET'])
def stop():
    gid = request.args.get('gid')
    tmp = aria2.get_download(gid)
    if tmp.status=='active' or 'paused':
        tmp.remove()
        return 'True'
    else:
        return 'False'


@app.route('/upload',methods = ['GET'])
def upload():
    return render_template('upload.html')

@app.route('/add-magnet',methods = ['GET'])
def download():
    magnet_uri = request.args.get('mag-link')
    gid = aria2.add_magnet(magnet_uri).gid
    return str(gid)

@app.route('/status',methods = ['GET'])
def status():
    gid = request.args.get('gid')
    new_gid=aria2.get_download(gid).followed_by_ids[0]
    file = aria2.get_download(new_gid)
    opt=''
    opt=opt+'Name: '+str(file.name)+'<br>'
    opt=opt+'Speed: '+str(file.download_speed_string())+'<br>'
    opt=opt+'D Speed: '+str(file.download_speed_string())+'<br>'
    opt=opt+'U Speed: '+str(file.upload_speed_string())+'<br>'
    opt=opt+'Progress: '+str(file.progress_string())+'<br>'
    opt=opt+'Total: '+str(file.total_length_string())+'<br>'
    return opt

@app.route('/drive/<arg>')
def action(arg):
        arg1=str(arg).replace('|','/')
        arg=arg+'|'
        ls1=[]
        ls2=[]
        ls3=[]
        ls4=[]
        #properties extract i.e folder or file
        tmp1=[]
        k=subprocess.Popen(["ls","-l","static/files/"+arg1],stdout=subprocess.PIPE).stdout
        for i in k:
            tmp1.append(str(i))
        tmp1=tmp1[1:]
        for i in tmp1:
            ls1.append(str(i).split("'")[1][0])
        #seq. me name load from system
        tmp2=[]
        k=subprocess.Popen(["ls","static/files/"+arg1],stdout=subprocess.PIPE).stdout
        for i in k:
            tmp2.append(str(i))
        for i in tmp2:
            ls2.append(str(i).split("'")[1].split("\\n")[0])
        #diffrent lists of files and folders
        for i in range(0,len(ls1)):
            if ls1[i]=='d':
                ls3.append(ls2[i])
            elif ls1[i]=='-':
                ls4.append(ls2[i])
        arg1=arg1+'/'
        return render_template('drive.html',list1=ls3,list2=ls4,arg=arg,arg1=arg1)

@app.route('/drive')
def files():
    ls1=[]
    ls2=[]
    ls3=[]
    ls4=[]

    #properties extract i.e folder or file
    tmp1=[]
    k=subprocess.Popen(["ls","-l","static/files"],stdout=subprocess.PIPE).stdout
    for i in k:
        tmp1.append(str(i))
    tmp1=tmp1[1:]
    for i in tmp1:
        ls1.append(str(i).split("'")[1][0])
    #seq. me name load from system
    tmp2=[]
    k=subprocess.Popen(["ls","static/files"],stdout=subprocess.PIPE).stdout
    for i in k:
        tmp2.append(str(i))
    for i in tmp2:
        ls2.append(str(i).split("'")[1].split("\\n")[0])
    #diffrent lists of files and folders
    for i in range(0,len(ls1)):
        if ls1[i]=='d':
            ls3.append(ls2[i])
        elif ls1[i]=='-':
            ls4.append(ls2[i])

    return render_template('drive.html',list1=ls3,list2=ls4)



  #return app.send_static_file(path)


if __name__ == '__main__':
    app.run(debug=True)
