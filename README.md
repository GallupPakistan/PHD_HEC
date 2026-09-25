# 📜 MapsScrapping Project - Setup Guide

This README provides complete instructions on how to:

* ✅ Commit code to GitHub using SSH
* ✅ Start and run the project on a Linux server using `.setup_map_scrapping.sh`
* ✅ Use common Linux commands to troubleshoot issues

---

## 🔧 Prerequisites

Before starting, make sure:

* You have added your **SSH public key** to your GitHub account.
* Your **private SSH key** is stored securely at:
  `/home/yourusername/.ssh/id_rsa` (with proper permissions: `chmod 600`)

---

## 🚀 How to Commit Code to GitHub (SSH)

### 1. Clone the repository (first-time setup)

```bash
git clone git@github.com:Ahmad-Umer/MapsScrapping.git
cd MapsScrapping
```

### 2. Check Git remote (ensure SSH)

```bash
git remote -v
```

You should see something like:

```
origin  git@github.com:Ahmad-Umer/MapsScrapping.git (fetch)
origin  git@github.com:Ahmad-Umer/MapsScrapping.git (push)
```

### 3. Make changes to your code

Edit your files normally. For example:

```bash
nano main.py
```

### 4. Add and commit your changes
#### When you want to push the new code to Github Repo, use the following commands
```bash
git status
git add . (To add all files)
git add <filename>
git commit -m "🔧 Updated scraping logic to handle new column format"
```

### 5. Push your changes to GitHub

```bash
git push origin main
```

You may be prompted for your SSH passphrase if one is set.

---

## 📆 How to Start the Project on a Linux Server

The project is designed to run via the `.setup.sh` script.

### 1. Connect to your server

```bash
ssh yourusername@your-server-ip
```

### 2. Run the setup script

```bash
cd /home/ahm3dum3r33
bash .setup_map_scrapping.sh
```

The script will:

* Export required environment variables
* Clone the latest code from GitHub using SSH
* Set up a Python virtual environment
* Activate the environment and run `main.py` with the correct configuration

### 3. Output

You’ll see environment variables printed, Git activity, and Python script logs.

---

## 🪠 Common Linux Commands for Troubleshooting

| Command                    | Purpose                                           |                                 |
| -------------------------- | ------------------------------------------------- | ------------------------------- |
| `nano`                     | To edit the file                                  |                                 |
| `cat`                      | To view the file                                  |                                 |
| `rm`                       | To remove the file                                |                                 |
| `echo $VARIABLE`           | Check if environment variables are set            |                                 |
| `env`                      | Print all environment variables                   |                                 |
| `which python3`            | Show the path of the installed Python interpreter |                                 |
| \`ps aux                   | grep python\`                                     | Check if your script is running |
| `tail -f /var/log/syslog`  | View live system logs                             |                                 |
| `chmod +x filename.sh`     | Make a `.sh` file executable                      |                                 |
| `ls -la`                   | Show detailed list of files with permissions      |                                 |
| `df -h`                    | Check disk space usage                            |                                 |
| `top` / `htop`             | Monitor CPU and memory usage                      |                                 |
| `deactivate`               | Exit a Python virtual environment                 |                                 |
| `source venv/bin/activate` | Activate virtual environment manually             |                                 |

---

## ❗ Troubleshooting Tips

* If environment variables are missing inside Python, ensure you're not using `sudo` **without** `--preserve-env`.
* To test SSH access to GitHub:

  ```bash
  ssh -i ~/.ssh/id_rsa git@github.com
  ```
* If Git asks for a username/password, you’re using HTTPS. Use SSH instead.

---

## 📬 Support

If you encounter issues, feel free to create a GitHub issue or reach out via email.
