const input = document.getElementById('cmdInput');
        const output = document.getElementById('output');
        const history = [];
        let historyIndex = -1;

        const commands = {
            help: () => [
                { type: 'success', text: 'Available commands:' },
                { type: 'info',    text: '  help     — show this help message' },
                { type: 'info',    text: '  clear    — clear the terminal' },
                { type: 'info',    text: '  date     — show current date & time' },
                { type: 'info',    text: '  whoami   — display current user' },
                { type: 'info',    text: '  echo ... — print text to terminal' },
            ],
            clear: () => { output.innerHTML = ''; return []; },
            date: () => [{ type: 'info', text: new Date().toString() }],
            whoami: () => [{ type: 'success', text: 'user (uid=1000, groups=sudo,docker)' }],
        };

        function addLine(text, type = 'info', delay = 0) {
            const line = document.createElement('div');
            line.className = `output-line ${type}`;
            line.style.animationDelay = `${delay}ms`;
            line.innerHTML = `<span class="line-prefix">›</span><span>${text}</span>`;
            output.appendChild(line);
            output.scrollTop = output.scrollHeight;
        }

        input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                const val = input.value.trim();
                if (!val) return;

                history.unshift(val);
                historyIndex = -1;

                // Echo the command
                addLine(`<span style="color:var(--accent)">user@~/home ❯</span> ${val}`, 'cmd');

                const [cmd, ...args] = val.split(' ');
                if (cmd === 'echo') {
                    addLine(args.join(' '), 'info', 50);
                } else if (commands[cmd]) {
                    const result = commands[cmd]();
                    result.forEach((r, i) => addLine(r.text, r.type, i * 60));
                } else {
                    addLine(`command not found: ${cmd}`, 'error', 50);
                    addLine(`Try <span style="color:var(--accent)">help</span> for available commands.`, 'info', 100);
                }

                input.value = '';
            }

            if (e.key === 'ArrowUp') {
                e.preventDefault();
                if (historyIndex < history.length - 1) {
                    historyIndex++;
                    input.value = history[historyIndex];
                }
            }

            if (e.key === 'ArrowDown') {
                e.preventDefault();
                if (historyIndex > 0) {
                    historyIndex--;
                    input.value = history[historyIndex];
                } else {
                    historyIndex = -1;
                    input.value = '';
                }
            }
        });

        // Auto-focus
        window.addEventListener('click', () => input.focus());
        input.focus();