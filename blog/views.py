from django.shortcuts import render, redirect
from django.utils import timezone
from django.contrib import auth
from .models import Post
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from django.views.decorators.csrf import csrf_exempt


import base64
import smtplib


def post_main(request):
    posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('published_date')
    return render(request, 'blog/post_main.html', {'posts': posts})


def logout(request):
    response = redirect('/')
    auth.logout(request)
    return response


def login(request):
    after_url = request.GET.get('next', '/')

    if request.method == "POST":
        username = request.POST['username'].strip()
        password = request.POST['password']
        user = auth.authenticate(request, username=username, password=password)

        if user is not None:
            auth.login(request, user)
            response = HttpResponseRedirect(after_url)
            return response
        else:
            return render(request, 'blog/post_main.html', {'error': '아이디와 비밀번호를 확인해주세요.'})

    else:
        return render(request, '/')


@csrf_exempt
def signup(request):
    if request.method == "POST":
        if request.POST["password1"] == request.POST["password2"]:

            if request.POST["usertype"] == "consumer":
                user = User.objects.create_user(username=request.POST["username"].strip(),
                                                password=request.POST["password1"].strip(),
                                                email=request.POST["username"].strip(),
                                                realname=request.POST["realname"].strip(),
                                                workplace=request.POST["workplace"],)
            elif request.POST["usertype"] == "expert":
                user = User.objects.create_user(username=request.POST["username"].strip(),
                                                password=request.POST["password1"].strip(),
                                                email=request.POST["username"].strip(),
                                                realname=request.POST["realname"].strip(),
                                                workplace=request.POST["workplace"],)

            auth.login(request, user)
            return redirect('/')

        elif request.POST["password1"] != request.POST["password2"]:
            return render(request, 'blog/signup.html', {'error': '비밀번호가 일치하지 않습니다. 확인해주세요.'})
    else:
        return render(request, 'blog/signup.html')


@csrf_exempt
def pswdmod(request):
    if request.method == "POST":
        username = request.POST["username"]
        key = 'heyvcc'

        try:
            User.objects.get(username=username)
            enc = []

            for i in range(len(username)):
                key_c = key[i % len(key)]
                enc_c = chr((ord(username[i]) + ord(key_c)) % 256)
                enc.append(enc_c)

            verify_code = base64.urlsafe_b64encode("".join(enc).encode()).decode().replace('=', '')

            if request.POST["verification"].strip() != verify_code.strip():

                gmail_sender = 'vccnet.owners@gmail.com'
                gmail_passwd = 'xhtmuimafstrqdsi'
                server = smtplib.SMTP('smtp.gmail.com', 587)
                server.ehlo()
                server.starttls()
                server.login(gmail_sender, gmail_passwd)

                msg = MIMEMultipart('alternative')
                msg['Subject'] = '[비밀번호 변경] 인증코드를 복사하여 입력해주세요.'
                msg['From'] = gmail_sender
                msg['To'] = username

                html = """\
                <!DOCTYPE html>
                <html>
                <body>

                <p>아래 인증 코드를 복사해서 입력해주세요.</p>
                인증코드<input type="text" style="width:450px;" value=""" + verify_code.strip() + """>
                <br>
                <br>
                <br>
                <br>
                <p>드래그 되지 않을 시</p><br>
                인증코드: """ + verify_code.strip() + """
                <p></p>

                </body>
                </html>
                """

                part2 = MIMEText(html, 'html')

                msg.attach(part2)

                server.sendmail(gmail_sender, [username], msg.as_string())
                server.quit()

                if request.POST["verification"].strip() != '':
                    errorMsg = '인증코드가 일치하지 않습니다. 인증 코드를 확인해주세요.'

                else:
                    errorMsg = username + '로 인증코드가 발송 되었습니다. 인증 코드를 입력해주세요.'

                return render(request, 'blog/post_main.html', {'username': username,
                                                             'pswdmoderror': errorMsg, })

            if request.POST["password1"] == request.POST["password2"]:
                u = User.objects.get(username__exact=request.POST["username"].strip())
                u.set_password(request.POST["password1"].strip())
                u.save()

                auth.login(request, u)
                return redirect('/')

            elif request.POST["password1"] != request.POST["password2"]:
                return render(request, 'blog/post_main.html', {'pswdmoderror': '비밀번호가 일치하지 않습니다. 확인해주세요.'})
        except:
            return render(request, 'blog/post_main.html', {'pswdmoderror': '존재하지 않는 계정입니다. 확인해주세요.'})
    else:
        return render(request, 'blog/post_main.html')
