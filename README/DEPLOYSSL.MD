Deploying a FastAPI application with HTTPS on an EC2 instance involves several steps. Here's a general guide:

```
sudo apt update
sudo apt install nginx
pip install uvicorn gunicorn fastapi
```

Configure Gunicorn: Create a Gunicorn configuration file for your FastAPI application. Replace main:app with the Python path to your FastAPI application instance.

`gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app`

Configure Nginx: Create a new Nginx configuration file in /etc/nginx/sites-available/ and link it to sites-enabled. The configuration should proxy pass to your Gunicorn server:

```
server {
    listen 80;
    server_name your_domain www.your_domain;

    location / {
        include proxy_params;
        proxy_pass http://unix:/tmp/gunicorn.sock;
    }
}
```

Obtain a SSL certificate: You can use Let's Encrypt to get a free SSL certificate. Install Certbot and the Nginx plugin with:
`sudo apt install certbot python3-certbot-nginx`

Then obtain the certificate with:
`sudo certbot --nginx`

Follow the prompts and Certbot will automatically configure Nginx to use the certificate.

Update Nginx configuration: After obtaining the certificate, update the Nginx configuration to listen on HTTPS:

```
server {
    listen 80;
    listen [::]:80;
    listen 443 ssl;
    listen [::]:443 ssl;

    server_name your_domain www.your_domain;

    location / {
        include proxy_params;
        proxy_pass http://unix:/tmp/gunicorn.sock;
    }

    ssl_certificate /etc/letsencrypt/live/your_domain/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your_domain/privkey.pem;
}
```

Start Gunicorn and Nginx: Finally, start the Gunicorn and Nginx services:
```
sudo service nginx start
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
```

Remember to replace your_domain with your actual domain name. Also, make sure your domain is pointing to the public IP address of your EC2 instance.