install:
	@echo "Installing the script to /usr/local/bin"
	cp optimize_compilation.py /usr/local/bin/optimize_compilation
	chmod +x /usr/local/bin/optimize_compilation
	@echo "Installation complete. You can now run 'optimize_compilation' from anywhere."

uninstall:
	@echo "Removing the script from /usr/local/bin"
	rm -f /usr/local/bin/optimize_compilation
	@echo "Uninstallation complete."

.PHONY: install uninstall
