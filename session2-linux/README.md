# 🐧 Session 2 - Linux Homework

> **Author:** Suhassk205  
> **Repo:** [devops-assignment](https://github.com/Suhassk205/devops-assignment)  
> **Session:** 2 - Linux Fundamentals

---

## 📋 Table of Contents

1. [Task 1: Soft Link & Hard Link](#task-1-soft-link--hard-link)
2. [Task 2: adduser vs useradd](#task-2-adduser-vs-useradd)
3. [Task 3: journalctl](#task-3-journalctl)
4. [Task 4: Linux Command Cheat Sheet](#task-4-linux-command-cheat-sheet)

---

## Task 1: Soft Link & Hard Link

### 🔍 What is a Hard Link?

A **hard link** is a direct pointer to the **inode** (actual data on disk) of a file. Both the original file and the hard link point to the **same inode**.

- Deleting the original file does **not** affect the hard link — the data still exists.
- Hard links **cannot** span across different filesystems/partitions.
- Hard links **cannot** be created for directories.

### 🔗 What is a Soft Link (Symbolic Link)?

A **soft link** (symlink) is a pointer to the **path/name** of the original file — like a shortcut in Windows.

- If the original file is deleted, the soft link becomes a **broken link**.
- Soft links **can** span across different filesystems.
- Soft links **can** point to directories.

---

### 📊 Comparison Table

| Feature | Hard Link | Soft Link |
|---|---|---|
| Points to | Inode (actual data) | File path/name |
| Original deleted? | Data still accessible | Link becomes broken |
| Cross filesystem? | ❌ No | ✅ Yes |
| Works on directories? | ❌ No | ✅ Yes |
| Size | Same as original | Small (just stores path) |
| Command | `ln` | `ln -s` |

---

### ⚙️ Commands

#### Creating a Hard Link
```bash
# Syntax
ln <original_file> <hard_link_name>

# Example
ln original.txt hardlink.txt

# Verify - both will show same inode number
ls -li original.txt hardlink.txt
```

#### Creating a Soft Link
```bash
# Syntax
ln -s <original_file> <soft_link_name>

# Example
ln -s original.txt softlink.txt

# Verify - soft link shows -> pointing to original
ls -li original.txt softlink.txt
```

#### Deleting Links
```bash
# Delete a soft link
unlink softlink.txt
# or
rm softlink.txt

# Delete a hard link
rm hardlink.txt
```

#### Practice Walkthrough
```bash
# 1. Create a test file
echo "Hello DevOps" > original.txt

# 2. Create hard link
ln original.txt hardlink.txt

# 3. Create soft link
ln -s original.txt softlink.txt

# 4. Check inodes
ls -li

# 5. Delete original and check
rm original.txt
cat hardlink.txt   # ✅ Works - hard link still has data
cat softlink.txt   # ❌ Broken - soft link is dead

# 6. Clean up
rm hardlink.txt softlink.txt
```

---

### 🎯 Interview Q&A

**Q: What is the difference between a hard link and a soft link?**  
> A hard link directly references the inode of a file, so data persists even if the original is deleted. A soft link references the file's path, so it breaks if the original is removed.

**Q: Can you create a hard link to a directory?**  
> No, hard links cannot be created for directories to avoid circular references in the filesystem.

**Q: What happens to a soft link when the original file is deleted?**  
> The soft link becomes a dangling/broken link and returns an error when accessed.

**Q: How can you identify an inode number of a file?**  
> Using `ls -i filename` or `stat filename`.

---

## Task 2: adduser vs useradd

### 🔍 What is `useradd`?

`useradd` is a **low-level binary** command available on all Linux distributions. It creates a user but does **not** automatically:
- Set a password
- Create a home directory (unless `-m` flag is used)
- Set default shell
- Copy skeleton files

### 🔍 What is `adduser`?

`adduser` is a **high-level Perl script** (on Ubuntu/Debian systems) that wraps around `useradd`. It:
- Automatically creates a home directory
- Prompts for a password interactively
- Copies skeleton files (`/etc/skel`)
- More user-friendly and interactive

---

### 📊 Comparison Table

| Feature | `useradd` | `adduser` |
|---|---|---|
| Type | Low-level binary | High-level script (Perl/bash) |
| Home directory | Not created by default | ✅ Created automatically |
| Password prompt | ❌ No | ✅ Yes |
| Skeleton files copied | ❌ No | ✅ Yes |
| Available on | All Linux distros | Ubuntu/Debian (mainly) |
| Preferred on Ubuntu? | ❌ Not recommended | ✅ Yes |
| Interactive? | ❌ No | ✅ Yes |

---

### ⚙️ Commands

#### Using `adduser` (Recommended on Ubuntu)
```bash
# Create a new user (interactive, sets password, home dir, etc.)
sudo adduser testuser

# The command will prompt for:
# - Password
# - Full name
# - Room number
# - Work phone
# - Home phone
# - Other info
```

#### Using `useradd` (Low-level)
```bash
# Basic (no home dir, no password)
sudo useradd testuser

# With home directory and default shell
sudo useradd -m -s /bin/bash testuser

# Set password separately
sudo passwd testuser
```

#### Create a Test User (Practice)
```bash
# Recommended way on Ubuntu
sudo adduser devops_test

# Verify user was created
id devops_test
cat /etc/passwd | grep devops_test

# Check home directory
ls /home/devops_test

# Switch to user
su - devops_test

# Delete user when done
sudo deluser --remove-home devops_test
```

---

### 🎯 Interview Q&A

**Q: What is the difference between `adduser` and `useradd`?**  
> `useradd` is a low-level binary that provides minimal user creation; you must manually set a password and home directory. `adduser` is a higher-level, interactive script that automatically creates a home directory, copies skeleton files, and prompts for a password.

**Q: Which command is preferred on Ubuntu and why?**  
> `adduser` is preferred on Ubuntu because it is more user-friendly, interactive, and automatically handles home directory creation and skeleton file setup.

**Q: How do you delete a user along with their home directory?**  
> `sudo deluser --remove-home <username>` on Ubuntu, or `sudo userdel -r <username>` with useradd.

---

## Task 3: journalctl

### 🔍 What is `journalctl`?

`journalctl` is a command-line tool used to **query and display logs** from the **systemd journal** (systemd's logging system). It collects logs from:
- The Linux kernel
- System services (daemons)
- Applications managed by systemd

> On modern Linux distros (Ubuntu 16.04+, CentOS 7+), systemd is the default init system and `journalctl` replaces older tools like `/var/log/messages`.

---

### ⚙️ Common Commands

#### View All Logs
```bash
# View all journal logs (oldest first)
journalctl

# View logs in reverse order (newest first)
journalctl -r
```

#### Follow Live Logs (like `tail -f`)
```bash
journalctl -f
```

#### View Logs for a Specific Service
```bash
# Syntax
journalctl -u <service_name>

# Examples
journalctl -u nginx
journalctl -u docker
journalctl -u ssh
journalctl -u cron
```

#### Filter by Time
```bash
# Logs since today
journalctl --since today

# Logs since a specific date
journalctl --since "2024-01-01 00:00:00"

# Logs between two timestamps
journalctl --since "2024-01-01" --until "2024-01-02"

# Last 1 hour
journalctl --since "1 hour ago"
```

#### Filter by Priority/Level
```bash
# Show only errors
journalctl -p err

# Show warnings and above
journalctl -p warning

# Priority levels: emerg, alert, crit, err, warning, notice, info, debug
```

#### Show Last N Lines
```bash
# Last 50 lines
journalctl -n 50

# Last 100 lines for a service
journalctl -u nginx -n 100
```

#### Kernel Logs Only
```bash
journalctl -k
```

#### Disk Usage of Journal
```bash
journalctl --disk-usage
```

#### Practice: Check Logs for a Specific Service
```bash
# 1. Check SSH service logs
journalctl -u ssh -n 20

# 2. Follow Docker logs live
journalctl -u docker -f

# 3. Check for errors in the last hour
journalctl -p err --since "1 hour ago"

# 4. Check cron job logs
journalctl -u cron --since today
```

---

### 🎯 Interview Q&A

**Q: What is `journalctl` used for?**  
> `journalctl` is used to query and display logs collected by the systemd journal. It provides a centralized way to view logs from the kernel, services, and applications.

**Q: How do you view logs for a specific service?**  
> Using `journalctl -u <service_name>`, e.g., `journalctl -u nginx`.

**Q: How do you follow live logs using journalctl?**  
> Using `journalctl -f`, which is similar to `tail -f`.

**Q: How do you filter logs by error level?**  
> Using `journalctl -p err` to show only error-level messages and above.

---

## Task 4: Linux Command Cheat Sheet

### 📁 File & Directory Commands

| Command | Description | Example |
|---|---|---|
| `ls` | List files and directories | `ls -la` |
| `pwd` | Print current working directory | `pwd` |
| `cd` | Change directory | `cd /home/user` |
| `mkdir` | Create a directory | `mkdir mydir` |
| `rmdir` | Remove empty directory | `rmdir mydir` |
| `rm` | Remove files/directories | `rm -rf mydir` |
| `cp` | Copy files/directories | `cp file1 file2` |
| `mv` | Move or rename files | `mv old.txt new.txt` |
| `touch` | Create empty file / update timestamp | `touch file.txt` |
| `cat` | Display file content | `cat file.txt` |
| `less` | View file content page by page | `less file.txt` |
| `head` | Show first N lines | `head -n 10 file.txt` |
| `tail` | Show last N lines | `tail -n 10 file.txt` |
| `find` | Search for files | `find / -name "file.txt"` |
| `locate` | Fast file search (uses DB) | `locate file.txt` |

---

### 🔐 File Permissions

| Command | Description | Example |
|---|---|---|
| `chmod` | Change file permissions | `chmod 755 script.sh` |
| `chown` | Change file owner | `chown user:group file.txt` |
| `ls -l` | View permissions | `ls -l file.txt` |
| `umask` | Set default permissions | `umask 022` |

#### Permission Notation
```
rwxrwxrwx
- Owner: rwx (read, write, execute)
- Group: rwx
- Others: rwx
- r=4, w=2, x=1 (e.g., chmod 755 = rwxr-xr-x)
```

---

### 👥 User Management

| Command | Description | Example |
|---|---|---|
| `adduser` | Add user (interactive, Ubuntu) | `sudo adduser john` |
| `useradd` | Add user (low-level) | `sudo useradd -m john` |
| `passwd` | Set/change password | `sudo passwd john` |
| `deluser` | Delete user | `sudo deluser john` |
| `userdel` | Delete user (low-level) | `sudo userdel -r john` |
| `usermod` | Modify user | `sudo usermod -aG sudo john` |
| `id` | Show user ID and groups | `id john` |
| `whoami` | Show current user | `whoami` |
| `su` | Switch user | `su - john` |
| `sudo` | Execute as superuser | `sudo apt update` |
| `groups` | Show groups of a user | `groups john` |
| `cat /etc/passwd` | View all users | `cat /etc/passwd` |

---

### 🔗 Links

| Command | Description | Example |
|---|---|---|
| `ln` | Create hard link | `ln file.txt hardlink.txt` |
| `ln -s` | Create soft/symbolic link | `ln -s file.txt softlink.txt` |
| `unlink` | Remove a link | `unlink softlink.txt` |
| `ls -li` | Show inode numbers | `ls -li` |

---

### 📊 System Info & Monitoring

| Command | Description | Example |
|---|---|---|
| `top` | Live process monitor | `top` |
| `htop` | Enhanced process monitor | `htop` |
| `ps` | List running processes | `ps aux` |
| `df` | Disk space usage | `df -h` |
| `du` | Directory disk usage | `du -sh /var` |
| `free` | Memory usage | `free -h` |
| `uptime` | System uptime | `uptime` |
| `uname` | System information | `uname -a` |
| `hostname` | Show/set hostname | `hostname` |
| `lscpu` | CPU information | `lscpu` |

---

### 🌐 Networking

| Command | Description | Example |
|---|---|---|
| `ip a` | Show IP addresses | `ip a` |
| `ip r` | Show routing table | `ip r` |
| `ping` | Test connectivity | `ping google.com` |
| `curl` | Transfer data from URLs | `curl https://example.com` |
| `wget` | Download files | `wget https://example.com/file` |
| `netstat` | Network statistics | `netstat -tulnp` |
| `ss` | Socket statistics (modern) | `ss -tulnp` |
| `nslookup` | DNS lookup | `nslookup google.com` |
| `dig` | DNS query tool | `dig google.com` |
| `traceroute` | Trace network path | `traceroute google.com` |

---

### 📦 Package Management (Ubuntu/Debian)

| Command | Description | Example |
|---|---|---|
| `apt update` | Update package list | `sudo apt update` |
| `apt upgrade` | Upgrade all packages | `sudo apt upgrade` |
| `apt install` | Install a package | `sudo apt install nginx` |
| `apt remove` | Remove a package | `sudo apt remove nginx` |
| `apt search` | Search for a package | `apt search nginx` |
| `dpkg -l` | List installed packages | `dpkg -l` |

---

### 🔍 Text Processing

| Command | Description | Example |
|---|---|---|
| `grep` | Search text in files | `grep "error" /var/log/syslog` |
| `awk` | Text processing tool | `awk '{print $1}' file.txt` |
| `sed` | Stream editor | `sed 's/old/new/g' file.txt` |
| `sort` | Sort lines | `sort file.txt` |
| `uniq` | Remove duplicates | `sort file.txt | uniq` |
| `wc` | Word/line count | `wc -l file.txt` |
| `cut` | Extract columns | `cut -d: -f1 /etc/passwd` |
| `tr` | Translate characters | `echo "HELLO" | tr 'A-Z' 'a-z'` |

---

### 📝 Logs

| Command | Description | Example |
|---|---|---|
| `journalctl` | View systemd logs | `journalctl -u nginx` |
| `journalctl -f` | Follow live logs | `journalctl -f` |
| `tail -f` | Follow a log file | `tail -f /var/log/syslog` |
| `cat /var/log/syslog` | View syslog | `cat /var/log/syslog` |
| `dmesg` | Kernel ring buffer logs | `dmesg | tail` |

---

### 🛠️ Process Management

| Command | Description | Example |
|---|---|---|
| `kill` | Kill a process by PID | `kill 1234` |
| `kill -9` | Force kill a process | `kill -9 1234` |
| `pkill` | Kill by process name | `pkill nginx` |
| `jobs` | List background jobs | `jobs` |
| `bg` | Resume job in background | `bg %1` |
| `fg` | Bring job to foreground | `fg %1` |
| `nohup` | Run command immune to hangup | `nohup ./script.sh &` |
| `&` | Run command in background | `./script.sh &` |

---

### ⌨️ Useful Shortcuts & Tips

```bash
# Redirect output to a file
command > output.txt      # Overwrite
command >> output.txt     # Append

# Pipe output to another command
command1 | command2

# Run multiple commands
command1 && command2      # Run command2 only if command1 succeeds
command1 || command2      # Run command2 only if command1 fails
command1 ; command2       # Run both regardless

# Search command history
history | grep ssh

# Clear terminal
clear   # or Ctrl+L

# Cancel a running command
Ctrl+C

# Suspend a command
Ctrl+Z

# Auto-complete
Tab key
```

---

## 📚 References & Resources

- [Linux Man Pages](https://man7.org/linux/man-pages/)
- [Ubuntu Documentation](https://ubuntu.com/server/docs)
- [journalctl Man Page](https://www.freedesktop.org/software/systemd/man/journalctl.html)
- [Linux File Permissions](https://chmod-calculator.com/)
- Session PDF: `basic-linux.pdf` / `ad-linux.pdf` *(included in this folder)*

---

> **Tip 💡:** Practice all commands in a safe Linux environment (VM, WSL, or Docker container) to build muscle memory!
