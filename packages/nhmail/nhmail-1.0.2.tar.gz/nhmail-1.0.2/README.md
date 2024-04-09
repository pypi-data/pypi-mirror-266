## SDK NAME : nhmail

### Sử dụng

```
pip install nhmail
from nhmail import MailWrapSystem
```

### Gửi email yêu cầu đặt lại mật khẩu:

body = 
```
{
    "to": <Email người nhận>,
    "template_data" : {
        "redirect_link":<Link cần redirect đến>,
        "user_name" : <Tên tài khoản>
    },
    "template_id":"d-3bcbc782a35d4a60848fd32be07ae9b5"
}
```
```
MailWrapSystem(body).send_verify_password()
```


### Gửi email chào mừng
body = 

```
{
    "to": <Email người nhận>,
    "template_data" : {
        "redirect_link":<Link cần redirect đến>,
        "user_name" : <Tên tài khoản>
    },
    "template_id":"d-71faed1a75c146d4b6363a2670c81e0b"
}
```
```
MailWrapSystem(body).send_welcome()
```

### Gửi email xác nhận nhân viên

body = 

```
{
    "to": <Email người nhận>,
    "template_data" : {
        "redirect_link":<Link cần redirect đến>,
        "user_name" : <Tên tài khoản>
    },
    "template_id":"d-3336da0dfd55433294ba17e6111278a6
}
```
```
MailWrapSystem(body).send_staff_confirm()
```