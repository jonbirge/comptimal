install:
	@echo "Installing the script to /usr/local/bin"
	cp optcom.py /usr/local/bin/optcom
	chmod +x /usr/local/bin/optcom
	@echo "Installation complete. You can now run 'optcom' from anywhere."

uninstall:
	@echo "Removing the script from /usr/local/bin"
	rm -f /usr/local/bin/optcom
	@echo "Uninstallation complete."

.PHONY: install uninstall
