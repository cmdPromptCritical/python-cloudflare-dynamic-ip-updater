To install and run the service, please execute the following commands:

   1. Move the service file:

   1     sudo mv /home/richard/prod/python-cloudflare-dynamic-ip-updater/cloudflare-dynamic-ip.service /etc/systemd/system/

   2. Reload the systemd daemon:

   1     sudo systemctl daemon-reload

   3. Enable the service to start on boot:
   1     sudo systemctl enable cloudflare-dynamic-ip.service

   4. Start the service now:
   1     sudo systemctl start cloudflare-dynamic-ip.service

  You can check the status of the service at any time with:

   1 sudo systemctl status cloudflare-dynamic-ip.service
