# Introduction 

In order to securely log in to remote computers using ssh, either a password or a key pair can be used. Key pairs are preferable for two reasons. Firstly, they are much much less vulnerable than passwords to being cracked by guessing, social engineering or brute-force attacks. Secondly, key pairs are usually set up to be used automatically, meaning that there is nothing extra you have to type in every time you use ssh.

Key pairs work by having **a private key that must be kept secret on your computer** and a paired **public key that can be distributed** to remote computers that you wish to access. The following instructions tell you how to generate a new key pair, install the private key on your computer, and **send the public key to the administrator of the computer** you wish to access.

# Instructions for Linux / MacOS / Windows 11 (/ 10\)

1. ## Open a terminal/shell

   1. **On macOS**: A terminal app is already part of the OS by default. Optionally you may want to install the XQuartz X server for graphical apps.  
      Open the Terminal application, which is located in Applications \-\> Utilities \-\> Terminal.app.  
   2. **On Linux / Unix**: A terminal app is already part of the OS by default and usually you also already have an X window server installed for graphical apps. Consult your distro (e.g. Ubuntu) documentation for details.  
   3. **On Windows 11**: A terminal app is already part of the OS by default: Open the Start menu, type Windows PowerShell, select Windows PowerShell, then select Open. (Of course you can also use Windows Subsystem for Linux (WSL) instead.)

2. ## Generate key pair

   1. **To generate a key pair with OpenSSH, type the following command:**  
      ```
      ssh-keygen -t ed25519 -C "your_comment_see_below"
      ``` 
      As a comment/label for your keys please use your `full name` followed by your `email address`. 

   2. **Select where to store the key pair**  
      The ssh-keygen application will now ask you where you want to save the private key:  
      ```
      Enter file in which to save the key (~/.ssh/id_ed25519): \<return\>  
      ```
      By default it will be stored in your `~/.ssh/` folder where `~` is your home directory. The public key will be stored in the same location as the private key, start with the same name as the private key and have a `.pub` suffix.

      **WARNING**:  
      Accepting the default will overwrite an existing key pair, so only accept the default if you either do not have a default key pair yet or if you want to replace your default key pair.  

      If you create a key pair in a non-default location, you will need to explicitly specify which key file to use when you start a session. Consult the [OpenSSH manual](https://www.openssh.com/manual.html) for details.

   3. **Secure the private key**  
      **Secure your private key with a good passphrase.** 
      
      DO NOT choose a simple passphrase or even worse an empty one\!  
      ```
      Enter passphrase (empty for no passphrase): <Type the passphrase\  
      ```

      Note: this is a passphrase to encrypt your private key. It is not a password for your account. Depending on your settings (option 3\. below), you should need to use this passphrase only once for your first use of ssh. All subsequent uses of ssh should be passphrase-free.  

      The ssh-keygen command will now generate two files. If you choose the default location these will be:  
      `Your private key in ~/.ssh/id_ed25519`

      `Your public key in ~/.ssh/id_ed25519.pub`

      The full path of `~/.ssh/` is usually:
      - Linux: `/home/<username>/.ssh/`  
      - MacOS: `/Users/<username>/.ssh/` 
      - Windows: `C:\\Users\\<username>/.ssh/`

3. ## (Optional) Adding your private SSH key to your ssh-agent

   Add your SSH private key to ssh-agent:

   ```
   ssh-add ~/.ssh/id_ed25519  
   ```
   This eliminates the need to re-enter the passphrase on every use.

   On Windows you might need to enable the ssh-agent service first. See detailed Windows SSH documentation [here](https://learn.microsoft.com/en-us/windows-server/administration/openssh/openssh_keymanagement)

4. ## Register your SSH public key 

   1. If the remote computer is managed by someone else:  
      1. (preferred) Attach the `~/.ssh/id_ed25519.pub` file to an email and send it to the administrator.  
      2. Or execute the following command and copy & paste the output in an email  
         ```
         cat ~/.ssh/id_ed25519.pub  
         ```
         and send the contents to the administrator.  
   2. If you manage the remote computer yourself:  
      1. Add the contents of `id_ed25519.pub` to the   
         ```
         ~/.ssh/authorized_keys  
         ```
         file of the relevant user, e.g. by running  
         ```
         cat id_ed25519.pub >> ~/.ssh/authorized_keys
         ```

