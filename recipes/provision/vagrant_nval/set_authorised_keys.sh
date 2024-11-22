#!/bin/bash

echo $(whoami)
echo $(pwd)
HOME="/home/vagrant"
# Check if the ~/.ssh/id_rsa.pub file exists
if [ -f "$HOME/.ssh/id_rsa.pub" ]; then
  # Get the contents of id_rsa.pub
  id_rsa_pub_content=$(cat "$HOME/.ssh/id_rsa.pub")
  
  # Append the content to the authorized_keys file in ~/.ssh directory
  if [ -d "$HOME/.ssh" ]; then
    echo $id_rsa_pub_content >> "$HOME/.ssh/authorized_keys"
    
    # Ensure there are no extra spaces at the beginning or end of the lines
    sed -i -e 's/^[ \t]*//g' -e 's/[ \t]*$//g' "$HOME/.ssh/authorized_keys"
    
    # Restrict file permissions for authorized_keys
    chmod 600 "$HOME/.ssh/authorized_keys"

    echo "SSH public key added to the list of authorized keys successfully."
  fi
else
  echo "~/.ssh/id_rsa.pub does not exist. Please generate your SSH key pair and add the public part (id_rsa.pub) to this directory."
fi
