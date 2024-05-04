"""Discord pagination mold for ranks"""
from typing import Any

import discord
from discord import Embed


def paginator(
    limit: int, max_per_page: int, embed_data: dict[Any],
    data: list[Any], data_vals: dict[str]
) -> list[Embed]:
    """Return filled paginator structure with data"""
    RANK_EMOJIS = ["<:LowHonor:1199342578085154886><:LowHonor:1199342578085154886><:LowHonor:1199342578085154886>",
                   "<:LowHonor:1199342578085154886><:LowHonor:1199342578085154886>",
                   "<:LowHonor:1199342578085154886>"]

    embeds = []
    limit_temp = limit

    # Maximum of <limit> number of rankings per embed page.
    rank_counter = 0
    while limit_temp > 0:
        curr_embed = discord.embeds.Embed.from_dict(embed_data)

        current_page = f"**Showing top {limit}**\n"
        num_per_page = 0
        if limit_temp >= max_per_page:
            num_per_page = max_per_page
        else:
            num_per_page = max_per_page - limit_temp

        # Append a line for the current page.
        for i in range(num_per_page):
            emoji = None
            match rank_counter + 1:
                case 1:
                    emoji = RANK_EMOJIS[0]
                case 2:
                    emoji = RANK_EMOJIS[1]
                case 3:
                    emoji = RANK_EMOJIS[2]

            object = None
            try:
                object = data[rank_counter]
            except IndexError:
                pass

            if object is None:
                current_page += f"**{rank_counter + 1}**) N/A\n"
            else:
                # Choosing what to put for each line based on command.
                command = data_vals["type"]
                if command == "topcounts":
                    line_with_emoji = (f"<:LowHonor:1199342578085154886> {object['member']} -"
                                       f" **{object['low_honor_word_count']:,}** low honor words\n")
                    line_without_emoji = (f"**{rank_counter + 1}**) {object['member']} - "
                                          f"**{object['low_honor_word_count']:,}** low honor words\n")
                if emoji:
                    current_page += f"{line_with_emoji}"
                else:
                    current_page += f"{line_without_emoji}"

            rank_counter += 1

        curr_embed.add_field(name="", value=current_page, inline=False)
        embeds.append(curr_embed)
        limit_temp -= 10
    return embeds
