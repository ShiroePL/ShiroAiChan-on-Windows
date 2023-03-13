import discord

def introduce_embed_fn():
    embed = discord.Embed(
        title="Shiro Chan is here!",
        description="I am AI streamer currently just chatting on discord cause I have free time :) . You can ask me anything!",
        color=discord.Colour.fuchsia() # Pycord provides a class with default colors you can choose from
    )
    embed.add_field(name="A Normal Field", value="A really nice field with some information. **The description as well as the fields support markdown!**")

    embed.add_field(name="Inline Field 1", value="Inline Field 1", inline=True)
    embed.add_field(name="Inline Field 2", value="Inline Field 2", inline=True)
    embed.add_field(name="Inline Field 3", value="Inline Field 3", inline=True)
 
    embed.set_footer(text="Footer! No markdown here.") # footers can have icons too
    embed.set_author(name="Shiro's Manager", icon_url="https://example.com/link-to-my-image.png")
    embed.set_thumbnail(url="https://example.com/link-to-my-thumbnail.png")
    #embed.set_image(file=discord.File('pictures/new_queen_on_chair.png'))
    
    return embed

__all__ = ['introduce_embed_fn']