[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-24ddc0f5d75046c5622901739e7c5dd533143b0c8e959d652212380cedb1ea36.svg)](https://classroom.github.com/a/M9yOg1uw)
# ketchUP video editor

### To pull the latest changes from the repository

git pull

### Admin Login Details 
username: admnin
password: 123456
\
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
- mysql> DESCRIBE Audio;
```
+---------------+----------+------+-----+---------+----------------+
| Field         | Type     | Null | Key | Default | Extra          |
+---------------+----------+------+-----+---------+----------------+
| AudioID       | int      | NO   | PRI | NULL    | auto_increment |
| AudioBlob     | longblob | YES  |     | NULL    |                |
| AudioMetadata | text     | YES  |     | NULL    |                |
+---------------+----------+------+-----+---------+----------------+
```
by 
```
CREATE TABLE Audio (
    AudioID INT AUTO_INCREMENT PRIMARY KEY,
    AudioBlob LONGBLOB,
    AudioMetadata TEXT
);
```
