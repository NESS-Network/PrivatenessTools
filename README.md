# PrivatenessTools
Console tools for working with Privateness service node.

Currently node and files services are supported.

Node service is for working with remote node.

Files service is for encrypted files storage.

All registration are done by Emercoin blockchain NVS.

All comunication between service node and client is encrypted and signed with ed25519 keypairs.

## Installation
* Required Python 3.10 +
`git clone https://github.com/NESS-Network/PrivatenessTools`

`pip install humanize requests pynacl pycryptodome prettytable validators lxml libxml2 libxslt random-word`

## Initialization
 * Generate user (keygen.py)
 * Register user in blockchain (`key.py nvs` and `key.py worm`)
 * Initialise local keys (key.py init)
 * Update nodes list (nodes-update.py)
 * Register in your node (python node.py set <node-name>)

## Running
* Any command can be runned `python command.py` or `./command`

## File system
### On service node
On service node all user files are stored in user's directory. There are no directories on service node, all user owned directories and real file names are stored on client. Here are the listin of files stored on service node:
```
user@robocop:~/Code/PrivatenessTools$ ./ls raw
 *** list *** 
+----------+------------------------------------------+---------+
| Filename | ID                                       | Size    |
+----------+------------------------------------------+---------+
| cgcu.94  | 84ac22776d99df2de55c4440609a7f9f9b73058c | 1244312 |
| dmsu.79  | 8c0f29eb08f96177188761490db9419c2b969d47 | 4690311 |
| gpte.61  | 782e579e92f85c2ed5526c1e418e5894dad4e2af | 4690023 |
| hnno.39  | b7e2187901e2257c3649b809c104186b66dc919a | 98531   |
| lgku.30  | 5672f1ec20b028f97903e5f2cb12a08b275e2230 | 1254024 |
| lpto.87  | 58cb5769261ac6f396e2c953b7c2298b010a9b1e | 4690023 |
| nlca.29  | 65bcf3ed2a7e241c4fce12012bc1cbc7b6882bae | 1244312 |
| swti.86  | f74010963816e7c4017f3a888e3b02849f3a4b47 | 6986349 |
| w.jpg    | 3f272cb9774bb9ad22b27ffa8acce114ad6f1c46 | 1244296 |
| yyze.67  | 69f5855cb9f21f1144f0ec01142a6f80b5e235f3 | 3322    |
+----------+------------------------------------------+---------+
```
`cgcu.94` is shadowname, this is a filename on service node, and a file is encrypted on client, each file is encrypted with it's own key. `w.jpg` is unencrypted file with custom shadowname=filename, this is a publicly shared file. Here is more informative file listing:
```
user@robocop:~/Code/PrivatenessTools$ ./ls
 *** Contents of 4: /555/qwerty  
+------------+----------+--------+---------+---------+-------------------------+
| Shadowname | Filename | Size   | Cipher  | Status  | Filepath                |
+------------+----------+--------+---------+---------+-------------------------+
| 5          | [..]     |        |         |         |                         |
| 6          | [pub]    |        |         |         |                         |
| cgcu.94    | w.jpg    | 1.2 MB | salsa20 | On Node | /home/user/Videos/w.jpg |
+------------+----------+--------+---------+---------+-------------------------+
user@robocop:~/Code/PrivatenessTools$ ./cd 6
user@robocop:~/Code/PrivatenessTools$ ./ls
 *** Contents of 6: /555/qwerty/pub  
+------------+----------+--------+--------+---------+-------------------------+
| Shadowname | Filename | Size   | Cipher | Status  | Filepath                |
+------------+----------+--------+--------+---------+-------------------------+
| 4          | [..]     |        |        |         |                         |
| w.jpg      | w.jpg    | 1.2 MB |        | On Node | /home/user/Videos/w.jpg |
+------------+----------+--------+--------+---------+-------------------------+
```
*4* *5* and *6* are directory ID's linked to directory names all stored on client. `cgcu.94` is encrypted file with original file name `w.jpg` and encrypted with `salsa20` and uploaded from `/home/user/Videos/w.jpg`.
Here is fileinfo for both files:
```
user@robocop:~/Code/PrivatenessTools$ ./fileinfo cgcu.94
 *** fileinfo *** 
+-------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| Param             | value                                                                                                                                                                                                            |
+-------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| File ID           | 84ac22776d99df2de55c4440609a7f9f9b73058c                                                                                                                                                                         |
| Filename          | w.jpg                                                                                                                                                                                                            |
| Shadowname        | cgcu.94                                                                                                                                                                                                          |
| Status            | On Node                                                                                                                                                                                                          |
| Filesize (local)  | 1.2 MB                                                                                                                                                                                                           |
| Filesize (remote) | 1.2 MB                                                                                                                                                                                                           |
| Filepath (local)  | /home/user/Videos/w.jpg                                                                                                                                                                                          |
| Cipher            | salsa20                                                                                                                                                                                                          |
| Encryption key    | Dvw]>?gsf}gKa%Ivc1.Tv[K6k8SEVVv9                                                                                                                                                                                 |
| Public link       | http://node-xxx.net/files/pub/84ac22776d99df2de55c4440609a7f9f9b73058c-a48d3a94dd9981fa1a091acf96833abc-I7FZSCFN7WNGQEBGRHX6YBRQT2DGGKI3I7PY2IHOF6AWA2WI6TV5VMS5FKKKTZTSFWFDB3OK6E3G5DLV7MPNBRUYCFJA3QKURHVIAAA= |
+-------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
user@robocop:~/Code/PrivatenessTools$ ./fileinfo w.jpg
 *** fileinfo *** 
+-------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| Param             | value                                                                                                                                                                                                            |
+-------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| File ID           | 3f272cb9774bb9ad22b27ffa8acce114ad6f1c46                                                                                                                                                                         |
| Filename          | w.jpg                                                                                                                                                                                                            |
| Shadowname        | w.jpg                                                                                                                                                                                                            |
| Status            | On Node                                                                                                                                                                                                          |
| Filesize (local)  | 1.2 MB                                                                                                                                                                                                           |
| Filesize (remote) | 1.2 MB                                                                                                                                                                                                           |
| Filepath (local)  | /home/user/Videos/w.jpg                                                                                                                                                                                          |
| Cipher            |                                                                                                                                                                                                                  |
| Encryption key    |                                                                                                                                                                                                                  |
| Public link       | http://node-xxx.net/files/pub/3f272cb9774bb9ad22b27ffa8acce114ad6f1c46-a48d3a94dd9981fa1a091acf96833abc-I7FZSCFN7WNGQEBGRHX6YBRQT2DGGKI3I7PY2IHOF6AWA2WI6TV5VMS5FKKKTZTSFWFDB3OK6E3G5DLV7MPNBRUYCFJA3QKURHVIAAA= |
+-------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
```

### On Client
On client all keys are stored in `~/privateness-keys/*.json` directory, directories are stored in `directories.json` and files are stored in `files.json`.

## Key generation
### ./keygen
```
*** PrivateNess KEY GENERATOR
### DESCRIPTION:
  Generates ciphers for NESS service nodes and NESS service node clients
  Works on ed25519 for keypairs
  Adjustable entropy when generating private keys
### USAGE:
#### Generate user Key
  user <username> "coma,separated,tags" <Entropy level>
  Example: $ ./keygen user user1 "Hello,World" 5
#### Generate node Key
  node <Node name or URL> <Tariff> master-user-name "coma,separated,services" "network"  <Entropy level>
  Example: $ ./keygen node http://my-node.net 111 master "prng,files" inet 5
#### Generate Faucet Key
  faucet <Faucet URL> <Entropy level>
  Example: $ ./keygen faucet http://www.faucet.net 5
#### Generate Backup Key
  backup <Entropy level>
  Example: $ ./keygen backup 5
#### Generate seed
  seed <length> <Entropy level>
  Example: $ ./keygen seed 32 5
#### Show this manual
  $ ./keygen help
  $ ./keygen -h
```
## Key management
### ./key
```
*** PrivateNess KEY UTILITY
### DESCRIPTION:
  Privateness keys infrastructure management
### USAGE:
### List Keys
#### Show all contents of keyfile
./key list [dirpath]
### Show Key
#### Show all contents of keyfile
./key show <keyfile>
#### show nvs name (for blockchain)
./key nvs <keyfile>
#### Show <worm> for blockchain (if there are any)
./key worm <keyfile>
#### Show all encrypted keys (if there are any)
./key list <keyfile>
### Pack keyfiles into encrypted keyfile
./key pack <keyfile1,keyfile2, ...> <encrypted keyfile>
### Unpack keyfiles from encrypted keyfile
./key unpack <encrypted keyfile>
### Save local keyfiles into encrypted keyfile
./key save <encrypted keyfile>
### Restore local keyfiles from encrypted keyfile
./key restore <encrypted keyfile>
### Eraise keyfile or all local keyfiles (fill with 0)
./key eraise [encrypted keyfile]

Keys directory: /home/user/.privateness-keys
```
## Node and user management
### ./nodes-update
```
*** Remote nodes update UTILITY
### DESCRIPTION:
  Service node list update from blockchain or remote node
### USAGE:
#### Update from blockchain (if RPC connection settings olready exist)
 ./nodes-update blockchain
 ./nodes-update blk
#### Update from remote node
 ./nodes-update node <remote-node-url>
#### Update from remote node (random node fron existing nodes list)
 ./nodes-update node
#### Auto update (try to update from random node, on error try to update from blockchain
./nodes-update
```
### ./node
```
*** Node manipulation
### USAGE:
#### List all nodes (previously fetched from blockchain or remote node):
 ./node list all
 ./node ls all
#### List all active nodes:
 ./node <list or ls> network service <+-s or +-t or +-q>
  network: inet yggdrasil tor i2p
  service: files or prng
  sorting:
   +-s free slots
   +-t tariff (coin hours)
   +-q file storage quota
   + ascending order
   - descending order
#### Set current node (you will be registered in that node):
 ./node sel <node-name>
#### Show about page
 ./node about <node-name>
#### Show info about node
 ./node info <node-name>
#### Show information about user on selected node
 ./node userinfo
```
### ./user
```
*** User list and user selection
### USAGE:
#### Show userlist
 ./user list|ls
#### Select user
 ./user sel|sl username
#### Check if current user is registered in blockchain
 ./user check|chk|ch
#### Show current user nvs
 ./user nvs
#### Show current user <WORM>
 ./user worm
#### Edit users file
 ./user edit [editor=nano]
```
### ./quota
```
*** User file usage quota
 ./quota
```

## Files

### ./upload
```
*** File upload
### USAGE:
#### Upload and encrypt file on service node
 ./upload enc <path to your file to upload>
 ./upload encrypt <path to your file to upload>
#### Upload file on service node with filename=shadowname
 ./upload <path to your file to upload>
 ./upload pub <path to your file to upload>
 ./upload public <path to your file to upload>
```
### ./download
```
*** File download
### USAGE:
#### Download file from service node
 ./download <file_shadowname> [path]
```
### ./jobs
```
*** File jobs
### USAGE:
#### List jobs
 ./jobs ls
 ./jobs list
#### Pause job
 ./jobs pause <file shadowname with current running job>
#### Resume job
 ./jobs run <file shadowname with current paused job>
```
### ./fileinfo
```
*** File info
### USAGE:
 ./fileinfo <file_shadowname>
```
### ./move
```
*** Move to other directory
### USAGE:
 ./move <File shadowname or Directory ID> <Directory ID>
```

## Directories
### ./ls
```
*** Current directory listing
### USAGE:
#### List files (current directory)
 ./ls
#### RAW list files (as they are stored on service node)
 ./ls raw
```
### ./cd
```
*** File info
### USAGE:
 ./cd <Directory ID>
```
### ./mkdir
```
*** Create directory
### USAGE:
 ./mkdir <parent directory ID> <directory name>
```
### ./move
```
*** Move to other directory
### USAGE:
 ./move <File shadowname or Directory ID> <Directory ID>
```
### ./tree
```
*** Directory tree
### USAGE:
#### List directories only
 ./tree
#### List directories with files
 ./tree files
```
### ./sync
 TODO ...

### ./backup
```
*** PrivateNess keys BACKUP
### Show backup SEED
 ./backup seed
### Show backup ADDRESS
 ./backup address
### Do backup to selected NODE or to FILE
 ./backup backup [filename]
### Restore backup from current NODE or from FILE
 ./backup restore [filename]
```