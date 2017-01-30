#Instructions

## Set up the environment
This project was developed under vagrant. Please use these steps below to initiate the project:
* run "vagrant up" to set up the virtualbox virtual machine and install the required packages.
* run "vagrant ssh" to log into the virtual machine.
* run "cd /vagrant" to switch to /vagrant folder.
* run "python lotsofitems.py" to initiate the sqlite database.
* finally run "python project.py" to start the web service.
    

## Test the "Item Catalog" project
After setting up the vagrant environment and start the web service, on the local machine, use the
browser to open "http://127.0.0.1:8000" URL.

The home page shows the categories and the latest items. Each category can be clicked to show the
list of items. Clicking each item presents the details of item information.

Users can browse the website anonymously with read-only right. Click the "login" button at the up-right
corner will redirect to Google+ sign-in page. After allowing the Google+ sign in, user can add items to
the database, and can also allow to edit or delete items created by the owner. User can click "logout"
button to logout of the website.

Visiting the urls below will get the JSON data:
* "http://127.0.0.1/catalog.json" will show the output all the categories and items information.
* "http://127.0.0.1/catalog/JSON" will show the output only the categories list information.
* "http://127.0.0.1/catalog/cat_id/JSON" will show the output the specific category's items information.
* "http://127.0.0.1/item/item_id/JSON" will show the output the specific item information.

