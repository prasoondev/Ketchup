[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-24ddc0f5d75046c5622901739e7c5dd533143b0c8e959d652212380cedb1ea36.svg)](https://classroom.github.com/a/M9yOg1uw)
# ketchUP video editor

### To pull the latest changes from the repository

git pull


### Running the Website

To run the project you first need to download npm.

For MacOS users, run brew install npm in the terminal.

For Linux users, run sudo apt install npm in the terminal.

Now you need to install express and bcrypt. Run the following commands.


npm install express
npm install bcrypt


To run the server, run node server.js with the directory where all the files are stored.

### Admin Login Details 
username: admninadmin
password: Abcd1234@

### Notes
- Use admin credentials to login
- Using the register command crashes the server which will be fixed in Milestone 2. 


### Milestone 2 

- Install all necessary mysql extensions such as flask-mysqldb, mysql-connector by using pip install in the venv (For Mac) or directly in Terminal for Linux users. 
- Create all tables as mentioned.
- mysql> DESCRIBE UserDetails;
```
+--------------+--------------+------+-----+---------+----------------+
| Field        | Type         | Null | Key | Default | Extra          |
+--------------+--------------+------+-----+---------+----------------+
| UserId       | int          | NO   | PRI | NULL    | auto_increment |
| UserName     | varchar(255) | NO   | UNI | NULL    |                |
| UserEmail    | varchar(255) | YES  | UNI | NULL    |                |
| UserPassword | varchar(255) | NO   |     | NULL    |                |
| UserImages   | varchar(255) | YES  |     | NULL    |                |
+--------------+--------------+------+-----+---------+----------------+
```
by 
```
CREATE TABLE Users (
    UserId INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    UserName VARCHAR(255) NOT NULL UNIQUE,
    UserEmail VARCHAR(255),
    UserPassword VARCHAR(255) NOT NULL,
    UserImages VARCHAR(255)
);
```
- mysql> DESCRIBE UserImages;
```
+---------------+--------------+------+-----+---------+-------+
| Field         | Type         | Null | Key | Default | Extra |
+---------------+--------------+------+-----+---------+-------+
| ImageId       | int          | NO   | PRI | NULL    |       |
| UserId        | int          | YES  |     | NULL    |       |
| ImageData     | mediumblob   | YES  |     | NULL    |       |
| ImageMetadata | varchar(255) | YES  |     | NULL    |       |
+---------------+--------------+------+-----+---------+-------+
```
by 
```
CREATE TABLE Images (
    ImageId INT NOT NULL PRIMARY KEY,
    UserId INT,
    ImageData MEDIUMBLOB,
    ImageMetadata VARCHAR(255)
);
```
