const sendMail = (app, to, subject, templateName, data) => {
    // Read the template file dynamically from templates directory
    const bytes = $os.readFile(`${__hooks}/templates/${templateName}.html`);
    let html = Buffer.from(bytes).toString('utf-8');

    // Inject variable values replacing {{key}} globally
    if (data && typeof data === 'object') {
        for (const key in data) {
            const value = data[key] || '';
            html = html.replace(new RegExp(`{{${key}}}`, 'g'), value);
        }
    }

    // Resolve sender settings from app configuration
    const fromAddress = app.settings().meta.senderAddress;
    const fromName = app.settings().meta.senderName || 'VetSentinel';

    // Normalize 'to' to array of MailerAddress objects
    let toArray = [];
    if (typeof to === 'string') {
        toArray = [{ address: to }];
    } else if (Array.isArray(to)) {
        toArray = to.map(item => {
            if (typeof item === 'string') return { address: item };
            return item;
        });
    } else if (to && typeof to === 'object') {
        toArray = [to];
    }

    const message = new MailerMessage({
        from: {
            address: fromAddress,
            name: fromName,
        },
        to: toArray,
        subject: subject,
        html: html,
    });

    app.newMailClient().send(message);
};

module.exports = {
    sendMail,
};
