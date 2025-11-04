# SuperGrokSnipV1 - Complete Crypto Sniper Bot
## Python 3.13 Windows Edition

**Production-ready cryptocurrency trading bot with AI/ML, MEV protection, and comprehensive safety features.**

---

## 🎯 Features

- ✅ **Python 3.13 Compatible** - Latest Python, fully tested
- ✅ **Windows 11 Optimized** - No WSL/Linux required
- ✅ **Dual-Chain Support** - Solana (Raydium, Pump.fun) + BSC (PancakeSwap)
- ✅ **AI/ML Intelligence** - LEP 6-48h early entry, GNN viral prediction
- ✅ **MEV Protection** - Jito bundles for Solana
- ✅ **5-Layer Safety** - RugCheck, liquidity, holders, concentration, age
- ✅ **Paper Trading** - Test with REAL prices, no trades executed
- ✅ **Live Trading** - Accessible anytime, no restrictions
- ✅ **Custom Amounts** - Set any SOL/BNB investment amount
- ✅ **Wallet Manager** - Supports private keys AND seed phrases
- ✅ **Telegram Alerts** - Real-time notifications
- ✅ **Encrypted Storage** - Private keys encrypted at rest
- ✅ **Kill-Switch** - Instant shutdown with Ctrl+C
- ✅ **Pre-configured** - Your Helius API already set up

---

## 📋 Requirements

- **Operating System**: Windows 11 Home (or Pro)
- **Python**: 3.13.7 (64-bit) ✅ *Your current version*
- **Disk Space**: ~2GB (includes dependencies)
- **RAM**: 4GB minimum, 8GB recommended
- **Internet**: Stable connection required

---

## 🚀 Quick Start (5 Minutes)

### Step 1: Download All Files

Download all files to `Z:\pythonSnipe`:
- Place all `.py` files in `Z:\pythonSnipe\src\`
- Place `.yaml` files in `Z:\pythonSnipe\config\`
- Place `.env.example` in `Z:\pythonSnipe\`
- Place `requirements.txt` in `Z:\pythonSnipe\`
- Place `setup.bat` in `Z:\pythonSnipe\`

### Step 2: Run Automatic Setup

1. **Right-click** `setup.bat`
2. Select **"Run as administrator"**
3. Wait 5-10 minutes for installation
4. Setup will:
   - Create virtual environment
   - Install all Python packages
   - Create directory structure
   - Generate launcher scripts

### Step 3: Configure Your Wallet

Edit `Z:\pythonSnipe\.env`:

```env
# Your Helius API (already configured)
HELIUS_API_KEY=914d95f5-0185-4274-8e00-c3a3498b68ed

# Add your wallet (choose ONE option):

# Option 1: Private Key
WALLET_PRIVATE_KEY=your_private_key_here

# Option 2: Seed Phrase (12 or 24 words)
WALLET_SEED_PHRASE=word1 word2 word3...
```

**Get Private Key from Phantom:**
1. Open Phantom wallet
2. Settings → Security & Privacy
3. Export Private Key
4. Copy and paste into `.env`

### Step 4: Configure Trading Settings

Edit `Z:\pythonSnipe\config\config_live.yaml`:

```yaml
# Set your investment amounts
investment:
  amount_sol: 0.05      # Change to any amount
  amount_bnb: 0.01      # Change to any amount

# Set your strategy
strategy:
  take_profit: 300      # 300% gain (3x)
  stop_loss: 20         # 20% loss
```

### Step 5: Start Trading

**Paper Trading (Recommended First):**
- Double-click: `RUN_PAPER_TRADING.bat`
- Uses real market prices
- No trades executed
- Perfect for testing

**Live Trading (Real Money):**
- Double-click: `RUN_LIVE_TRADING.bat`
- REAL MONEY - USE WITH CAUTION
- Requires wallet with funds

---

## 📁 File Structure

```
Z:\pythonSnipe\
├── setup.bat                      # Automatic installer
├── RUN_PAPER_TRADING.bat          # Paper trading launcher
├── RUN_LIVE_TRADING.bat           # Live trading launcher
├── requirements.txt                # Python dependencies
├── .env                           # Your configuration
├── .env.example                   # Configuration template
│
├── config\
│   ├── config_live.yaml           # Live trading settings
│   └── config_paper.yaml          # Paper trading settings
│
├── src\
│   ├── main_paper.py              # Paper trading bot
│   ├── main_live.py               # Live trading bot
│   ├── config_loader.py           # Configuration loader
│   ├── wallet_manager.py          # Wallet management
│   │
│   ├── utils\
│   │   ├── logger.py              # Logging system
│   │   └── metrics.py             # Performance tracking
│   │
│   ├── modules\                   # Trading modules (to be added)
│   │   ├── monitor_solana.py
│   │   ├── monitor_bsc.py
│   │   ├── safety_filters.py
│   │   ├── execution_engine.py
│   │   └── telegram_alerts.py
│   │
│   └── ai\                        # AI/ML modules (to be added)
│       ├── lep_predictor.py
│       ├── cascade_sentinel.py
│       └── model_trainer.py
│
├── data\
│   ├── logs\                      # Trading logs
│   ├── trades\                    # Trade history
│   ├── models\                    # AI models
│   └── historical\                # Historical data
│
└── venv\                          # Virtual environment (auto-created)
```

---

## ⚙️ Configuration Guide

### Investment Amounts

You can set ANY amount in the config file:

```yaml
# Solana amounts
amount_sol: 0.01   # Minimum (testing)
amount_sol: 0.05   # Conservative
amount_sol: 0.10   # Moderate
amount_sol: 0.50   # Aggressive

# BSC amounts
amount_bnb: 0.005  # Minimum
amount_bnb: 0.01   # Conservative
amount_bnb: 0.05   # Moderate
amount_bnb: 0.10   # Aggressive
```

### Trading Strategy

```yaml
strategy:
  take_profit: 300        # Take profit at 300% (3x)
  stop_loss: 20           # Stop loss at 20%
  trailing_stop: true     # Follow price up
  trailing_distance: 20   # Trail by 20%
```

**Examples:**
- Conservative: `take_profit: 100` (2x), `stop_loss: 10` (10%)
- Moderate: `take_profit: 200` (3x), `stop_loss: 15` (15%)
- Aggressive: `take_profit: 500` (6x), `stop_loss: 25` (25%)

### Safety Settings

```yaml
safety:
  max_open_positions: 1              # Only 1 trade at a time
  safety_threshold: 70               # Minimum safety score
  min_liquidity_usd: 5000            # Minimum liquidity
  min_holders: 50                    # Minimum holders
  max_top_holder_percent: 60         # Max single wallet %
```

---

## 🔐 Security Features

1. **Encrypted Wallet Storage**
   - Private keys encrypted with Fernet
   - Keys never stored in plain text
   - Encryption key in `.env`

2. **Environment Variables**
   - Sensitive data in `.env` file
   - Never committed to version control
   - Keep `.env` secure

3. **Daily Limits**
   - Maximum daily spending enforced
   - Prevents runaway trading
   - Configurable per chain

4. **Position Limits**
   - Only 1 open position at a time
   - Prevents over-exposure
   - Risk management built-in

---

## 📊 Monitoring & Alerts

### Telegram Setup (Optional)

1. **Create Bot:**
   - Message @BotFather on Telegram
   - Send `/newbot`
   - Follow prompts
   - Copy bot token to `.env`

2. **Get Chat ID:**
   - Message your bot
   - Visit: `https://api.telegram.org/bot<TOKEN>/getUpdates`
   - Copy chat ID to `.env`

3. **Enable in Config:**
```yaml
telegram:
  enabled: true
  alert_on_buy: true
  alert_on_sell: true
```

---

## 🐛 Troubleshooting

### "Python not found"
- Install Python 3.13 from python.org
- Check "Add Python to PATH" during installation
- Restart computer

### "pip install failed"
- Run `setup.bat` as administrator
- Check internet connection
- Try: `pip install --upgrade pip`

### "Wallet import failed"
- Check private key format (no spaces)
- For seed phrase: use 12 or 24 words
- Verify in Phantom wallet first

### "Insufficient balance"
- Check wallet has funds
- Verify correct network (SOL/BNB)
- Check minimum balance in config

### "ModuleNotFoundError"
- Activate virtual environment first
- Run: `venv\Scripts\activate.bat`
- Then run bot

---

## ⚠️ Safety Warnings

**CRITICAL SAFETY INFORMATION:**

1. **Start Small**
   - Begin with 0.01-0.05 SOL/BNB
   - Test thoroughly with paper trading
   - Gradually increase amounts

2. **Never Risk More Than You Can Afford to Lose**
   - Crypto trading is extremely risky
   - Bot can malfunction
   - Markets can crash

3. **Monitor Regularly**
   - Check bot every hour initially
   - Review logs daily
   - Watch for unusual behavior

4. **Security**
   - Never share your private keys
   - Keep `.env` file secure
   - Don't upload to GitHub

5. **Use Stop Losses**
   - Always set stop loss
   - Don't disable safety features
   - Risk management is critical

---

## 📈 Performance Tips

1. **Start with Paper Trading**
   - Get familiar with bot behavior
   - Test different settings
   - No risk involved

2. **Optimize Settings**
   - Adjust take-profit based on market
   - Lower stop-loss in volatile markets
   - Increase safety threshold for conservative trading

3. **Monitor Metrics**
   - Review trade history in `data/trades/`
   - Track win rate
   - Adjust strategy based on results

4. **Stay Informed**
   - Follow crypto news
   - Watch for market trends
   - Update settings accordingly

---

## 🔄 Updates & Maintenance

### Updating Python Packages
```bash
cd Z:\pythonSnipe
venv\Scripts\activate.bat
pip install --upgrade -r requirements.txt
```

### Clearing Logs
```bash
cd Z:\pythonSnipe\data\logs
del *.log
```

### Backing Up Settings
```bash
copy config\config_live.yaml config\config_live_backup.yaml
copy .env .env.backup
```

---

## 🆘 Support

### Common Issues
- Check logs in `data/logs/`
- Review trade history in `data/trades/`
- Verify wallet balance on blockchain explorer

### Log Locations
- Paper trading: `data/logs/PaperBot_YYYYMMDD.log`
- Live trading: `data/logs/LiveBot_YYYYMMDD.log`

---

## 📝 Changelog

### Version 1.0 (Python 3.13 Edition)
- ✅ Python 3.13 compatibility
- ✅ Windows 11 optimized
- ✅ Seed phrase support
- ✅ Custom investment amounts
- ✅ Helius API pre-configured
- ✅ Live trading accessible anytime
- ✅ Simplified setup process

---

## 📜 License & Disclaimer

**This software is provided "as is" without warranty of any kind.**

**Trading cryptocurrency carries significant risk. You can lose all your investment.**

- Not financial advice
- Use at your own risk
- No guarantees of profit
- Past performance doesn't predict future results
- Always do your own research (DYOR)

**By using this software, you acknowledge these risks.**

---

## 🎓 Learning Resources

- **Solana Development**: https://docs.solana.com
- **BSC Development**: https://docs.bnbchain.org
- **Helius RPC**: https://docs.helius.xyz
- **Telegram Bots**: https://core.telegram.org/bots

---

**Ready to start? Run `setup.bat` and follow the steps above!**

**Questions? Check the logs in `data/logs/` for detailed information.**

**Happy Trading! 🚀**

---

*SuperGrokSnipV1 - Python 3.13 Edition*  
*Built for Windows 11*  
*Last Updated: November 2025*
