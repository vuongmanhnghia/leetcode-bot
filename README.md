# 🤖 LeetCode Discord Bot

A Discord bot that automatically creates daily LeetCode challenges and posts them as threads in your Discord server.

## ✨ Features

-  **🔄 Daily Challenges**: Automatically creates LeetCode challenges every day
-  **🧵 Thread Management**: Creates organized Discord threads for each challenge
-  **📊 Problem Crawling**: Fetches problem details from LeetCode's GraphQL API
-  **🎨 Beautiful Formatting**: Formats problems with difficulty indicators and examples
-  **⚡ Caching**: Intelligent caching for better performance
-  **🛠️ Manual Testing**: Commands to test thread creation immediately

## 🚀 Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Environment Configuration

Create `.env` file:

```env
DISCORD_BOT_TOKEN=your_discord_bot_token
CHANNEL_ID=your_discord_channel_id
DAILY_TIME=07:00
TIMEZONE_OFFSET=+7
```

### 3. Initialize Data

```bash
echo "1" > current_problem.txt
```

### 4. Run Bot

```bash
python main.py
```

## 📋 Commands

-  **`/test_dsa`**: Create a test DSA thread immediately (requires "Manage Threads" permission)

## 🏗️ Architecture

-  **`main.py`**: Main bot with Discord events and scheduled tasks
-  **`bot_config.py`**: Bot configuration and Discord client setup
-  **`crawl_api.py`**: LeetCode API crawler with GraphQL integration
-  **`leetcode_integration.py`**: High-level LeetCode integration
-  **`analyst.py`**: CSV data loading utilities

## 🔧 Configuration

| Variable            | Description                       | Required |
| ------------------- | --------------------------------- | -------- |
| `DISCORD_BOT_TOKEN` | Discord bot token                 | ✅       |
| `CHANNEL_ID`        | Target Discord channel ID         | ✅       |
| `DAILY_TIME`        | Time for daily challenges (HH:MM) | ❌       |
| `TIMEZONE_OFFSET`   | Timezone offset                   | ❌       |

## 🎨 Content Formatting

The bot formats problems with:

-  Difficulty indicators (🟢 Easy, 🟡 Medium, 🔴 Hard)
-  Topic tags and examples
-  Constraints and follow-up questions
-  Embedded images and code blocks

## 🧪 Testing

```bash
python test.py
```

## 🔒 Security

-  Environment variables for sensitive data
-  Permission checks for commands
-  Graceful error handling

## 🚨 Troubleshooting

1. **Bot Not Starting**: Check `DISCORD_BOT_TOKEN`
2. **Thread Creation Fails**: Verify bot permissions
3. **API Errors**: Check internet connection and LeetCode API status

---

**Happy Coding! 🚀**
