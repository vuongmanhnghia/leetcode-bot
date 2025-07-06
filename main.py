import random
from datetime import datetime, timedelta
from typing import Dict

import discord
from discord.ext import tasks

from analyst import get_url_from_data, load_leetcode_data
from bot_config import DISCORD_BOT_TOKEN, bot

leetcode_data = load_leetcode_data("leetcode_data.csv")


def format_daily_challenge(problem: Dict) -> str:
    """Format daily challenge content"""
    today = datetime.now()

    content = f"""*📌 # LeetCode Daily Challenge ({today.strftime('%d/%m/%Y')})*

{bot.leetcode.format_problem_for_discord(problem)}

**GOOD LUCK CODING! 🚀**

"""
    return content


async def check_permission(interaction) -> bool:
    if not interaction.guild or not (interaction.user.guild_permissions.manage_threads if hasattr(interaction.user, "guild_permissions") else False):  # type: ignore
        await interaction.response.send_message(
            "❌ Bạn cần quyền quản lý thread để sử dụng lệnh này!", ephemeral=True
        )
        return False
    return True


@bot.event
async def on_ready():
    """When bot is ready"""
    print(f"🤖 {bot.user} đã kết nối thành công!")
    print(f"🌐 Đang phục vụ {len(bot.guilds)} server(s)")

    if not daily_dsa_task.is_running():
        daily_dsa_task.start()


@tasks.loop(hours=24)
async def daily_dsa_task():
    """Daily task to create DSA thread"""
    if not bot.config.get("CHANNEL_ID"):
        print("❌ Chưa cấu hình CHANNEL_ID")
        return

    try:
        channel = bot.get_channel(bot.config["CHANNEL_ID"])
        if not channel or not isinstance(channel, discord.TextChannel):
            print(f"❌ Không tìm thấy text channel với ID: {bot.config['CHANNEL_ID']}")
            return

        problem_id = bot.leetcode.get_daily_challenge()
        if not problem_id:
            print("❌ Lỗi khi lấy bài toán hàng ngày")
            return

        problem = await crawl_problem(problem_id)
        if not problem:
            print("❌ Lỗi khi crawl bài toán từ LeetCode!")
            return

        today = datetime.now()
        thread_name = f"🧪 **LeetCode - {today.strftime('%d/%m')} - {problem['title']} - {problem['difficulty']}**"

        thread = await channel.create_thread(
            name=thread_name, reason="Daily DSA Challenge"
        )

        msg = await channel.send(f"{thread_name}")

        thread = await msg.create_thread(
            name=thread_name, auto_archive_duration=60, reason="Test DSA Challenge"
        )

        content = format_daily_challenge(problem)
        await thread.send(content)

        print(f"✅ Đã tạo thread: {thread_name}")

    except Exception as e:
        print(f"❌ Lỗi khi tạo thread: {e}")


@daily_dsa_task.before_loop
async def before_daily_task():
    """Wait until specified time to run task"""
    await bot.wait_until_ready()

    now = datetime.now()
    target_time = datetime.strptime(
        bot.config.get("DAILY_TIME", "07:00"), "%H:%M"
    ).time()
    next_run = datetime.combine(now.date(), target_time)

    if next_run <= now:
        next_run += timedelta(days=1)

    await discord.utils.sleep_until(next_run)


@bot.tree.command(name="test_dsa", description="Tạo thread DSA test ngay lập tức")
async def test_thread(interaction: discord.Interaction):
    """Test creating a DSA thread immediately"""
    has_permission = await check_permission(interaction)
    if has_permission == False:
        return

    if not isinstance(interaction.channel, discord.TextChannel):
        await interaction.response.send_message(
            "❌ Lệnh này chỉ có thể sử dụng trong text channel!", ephemeral=True
        )
        return

    try:
        await interaction.response.defer()

        problem_id = random.randint(1, 100)
        problem = await crawl_problem(problem_id)

        if not problem:
            await interaction.followup.send("❌ Lỗi khi crawl bài toán từ LeetCode!")
            return

        today = datetime.now()
        thread_name = f"🧪 **LeetCode - {today.strftime('%d/%m')} - {problem['title']} - {problem['difficulty']}**"

        # Gửi message vào channel trước để tạo thread public
        msg = await interaction.channel.send(f"{thread_name}")
        thread = await msg.create_thread(
            name=thread_name, auto_archive_duration=60, reason="Test DSA Challenge"
        )

        content = format_daily_challenge(problem)
        await thread.send(content)

        await interaction.followup.send(
            f"✅ Đã tạo thread: {thread.mention}",
            ephemeral=True,  # hoặc False nếu muốn mọi người đều thấy
        )

    except Exception as e:
        print(f"❌ Lỗi khi tạo thread test: {str(e)}")


async def crawl_problem(problem_id):
    try:
        url = get_url_from_data(leetcode_data, problem_id)

        problem = bot.leetcode.add_problem_by_url(url)
        if not problem:
            print("❌ Không thể crawl bài toán từ URL này!")
            return
        return problem

    except Exception as e:
        print(f"❌ Lỗi khi crawl bài toán: {str(e)}")


@bot.tree.error
async def on_app_command_error(
    interaction: discord.Interaction, error: discord.app_commands.AppCommandError
):
    """Handle command errors"""
    if isinstance(error, discord.app_commands.CommandOnCooldown):
        await interaction.response.send_message(
            f"⏰ Lệnh đang trong cooldown. Thử lại sau {error.retry_after:.2f}s",
            ephemeral=True,
        )
    else:
        await interaction.response.send_message(f"❌ Lỗi: {str(error)}", ephemeral=True)


if __name__ == "__main__":
    bot.run(DISCORD_BOT_TOKEN)
