const { default: makeWASocket, useMultiFileAuthState, DisconnectReason } = require('@whiskeysockets/baileys');
const express = require('express');
const qrcode = require('qrcode');
const pino = require('pino');
const fs = require('fs');
const path = require('path');

const app = express();
app.use(express.json());

let sock = null;
let qrCodeData = null;
let connectionStatus = 'Disconnected';

async function connectToWhatsApp() {
    const authFolder = path.join(__dirname, 'auth_info_baileys');
    const { state, saveCreds } = await useMultiFileAuthState(authFolder);
    
    sock = makeWASocket({
        auth: state,
        logger: pino({ level: 'silent' }), // Hide noisy debug logs
        printQRInTerminal: true
    });
    
    sock.ev.on('creds.update', saveCreds);
    
    sock.ev.on('connection.update', (update) => {
        const { connection, lastDisconnect, qr } = update;
        
        if (qr) {
            qrcode.toDataURL(qr, (err, url) => {
                if (!err) {
                    qrCodeData = url;
                }
            });
            connectionStatus = 'Waiting for scan';
        }
        
        if (connection === 'close') {
            const shouldReconnect = lastDisconnect?.error?.output?.statusCode !== DisconnectReason.loggedOut;
            console.log('Connection closed due to: ', lastDisconnect?.error?.message || lastDisconnect?.error, '. Reconnecting: ', shouldReconnect);
            connectionStatus = 'Disconnected';
            qrCodeData = null;
            if (shouldReconnect) {
                setTimeout(connectToWhatsApp, 5000); // Wait 5s before reconnecting
            }
        } else if (connection === 'open') {
            console.log('WhatsApp connection opened successfully!');
            connectionStatus = 'Connected';
            qrCodeData = null;
        }
    });
}

// API to check status and get QR code
app.get('/status', (req, res) => {
    res.json({
        status: connectionStatus,
        qr: qrCodeData
    });
});

// API to send message
app.post('/send', async (req, res) => {
    const { to, message } = req.body;
    if (!to || !message) {
        return res.status(400).json({ error: 'Missing "to" or "message" parameters' });
    }
    
    if (connectionStatus !== 'Connected') {
        return res.status(500).json({ error: 'WhatsApp is not connected yet.' });
    }
    
    try {
        let formattedPhone = to.toString().replace(/\D/g, '');
        if (formattedPhone.length === 10) {
            formattedPhone = '91' + formattedPhone;
        }
        const jid = `${formattedPhone}@s.whatsapp.net`;
        
        await sock.sendMessage(jid, { text: message });
        res.json({ success: true });
    } catch (err) {
        console.error('Failed to send message:', err);
        res.status(500).json({ error: err.message });
    }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, '0.0.0.0', () => {
    console.log(`WhatsApp API Gateway running on port ${PORT}`);
    connectToWhatsApp();
});
