const express = require('express');
const bodyParser = require('body-parser');
const path = require('path');
const fs = require('fs');
const bcrypt = require('bcrypt');

const app = express();
const PORT = process.env.PORT || 3000;

app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

app.use(express.static(path.join(__dirname, 'public')));

const DataBase = 'dataBase.txt';

let username = '';

function hashPasswordAndAppend(username, passwordToHash) {
    const saltRounds = 10;
        bcrypt.hash(passwordToHash, saltRounds, (err, hash) => {
        if(err) {
            console.error('Error hashing password:', err);
        }
        else {
            const data = username + ':' + hash + '\n';
            appendToFile(DataBase, data);
        }
    });
}

async function comparePasswords(passwordToCheck, hashedPassword) {
    try {
        const res = await bcrypt.compare(passwordToCheck, hashedPassword);
        return res;
    }
    catch (error) {
        console.error('Error comparing passwords:', error);
        return false;
    }
}

function isLoggedIn(req, res, next) {
    if(username === '') {
        res.status(401).json({error: 'Unauthorized: Access Denied'});
    }
    else {
        next();
    }
}

app.get('/api/CheckLogin', isLoggedIn, (req, res) => {
    res.json({success: true, message: 'Access granted'});
});

function readFromFile(filePath) {
    fs.readFile(filePath, 'utf8', (err, data) => {
        if(err) {
            const contentToWrite = '[\n\n]';
            data = contentToWrite;
            fs.writeFile(filePath, contentToWrite, 'utf8', (writeErr) => {
                if (writeErr) {
                    console.error('Error creating file:', writeErr);
                }
            });
        }
        const parsedData = JSON.parse(data);
        userTodoList = parsedData;
        return parsedData;
    });
}

async function searchFile(filePath, username, password, checkPasssword) {
    try {
        if(!fs.existsSync(filePath)) {
            fs.writeFileSync(filePath, '');
        }
        const data = fs.readFileSync(filePath, 'utf8');

        const allUsers = data.split('\n');
        const regex = /^(.*?):(.*)$/;

        for(const currentUser of allUsers) {
            const match = currentUser.match(regex);
            console.log(match[1]);
            if(match) {
                const currentUsername = match[1];
                const currentPassword = match[2];
                const passwordsMatch = await comparePasswords(password, currentPassword);
                if(username === currentUsername && passwordsMatch) {
                    return true;
                }
                if(username === currentUsername && !checkPasssword) {
                    return true;
                }
            }
        }
        return false;
    }
    catch {
        console.error('Error reading file:', err);
    }
}

function appendToFile(filePath, data) {
    if(!fs.existsSync(filePath)) {
        fs.writeFileSync(filePath, '');
    }
    fs.appendFile(filePath, data, 'utf8', (err) => {
        if (err) {
            console.error('Error appending to file:', err);
        }
    });
}

app.get('/api/GetUser', (req, res) => {
    if(username == '') {
        res.json({success: false, message: 'No user found.'});
    }
    else {
        res.json({success: true, message: username});
    }
});

app.post('/api/LogoutUser', (req, res) => {
    username = '';
    res.json({success: true});
});

app.post('/api/LoginUser', async (req, res) => {
    let result = await searchFile(DataBase, req.body.username, req.body.password, true);
    if(result == true) {
        username = req.body.username;
        res.json({success: true, message: 'Logged in successfully.'});
    }
    else {
        res.json({success: false, message: 'Incorrect username/password.'});
    }
});

app.post('/api/RegisterUser', async (req, res) => {
    let username_taken = false, noNumber = true, noSpecial = true, noCapital = true, length = false;
    username_taken = await searchFile(DataBase, req.body.username, '', false);
    length = (req.body.password.length < 8) ? true : false;
    req.body.password.split('').forEach(function(currentCharacter) {
        if(currentCharacter >= '0' && currentCharacter <= '9') {
            noNumber = false;
        }
        else if(currentCharacter >= 'A' && currentCharacter <= 'Z') {
            noCapital = false;
        }
        else if(currentCharacter < 'a' || currentCharacter > 'z') {
            noSpecial = false;
        }
    });
    if(!username_taken && !noNumber && !noSpecial && !noCapital && !length) {
        hashPasswordAndAppend(req.body.username, req.body.password);
        res.json({success: true, message: 'Username added. Please login'});
    }
    else {
        res.json({success: false, message: 'The following do not match', username_taken: username_taken, number: noNumber, special: noSpecial, capital: noCapital, length: length});
    }
});

app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});