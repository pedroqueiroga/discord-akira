from bidict import bidict

translation_book = bidict({
    'miaau.': 'Talvez mais tarde.',
    'MIAAAU!!!': 'Você não está em nenhum canal de voz.',
    'Miau...': 'Você não está no meu canal de voz.',
    'Miau.': 'Pulei.',
    'Meow.': 0,
    'miau?': 1,
    'miiau!': 2,
    'miiiau!!': 3,
    'mivau.': 4,
    'MVAU.': 5,
    'mviau.': 6,
    'mviiau.': 7,
    'MViiIAU!': 8,
    'mixau.': 9,
    '...': 'Fila vazia.',
    '...?': 'Não estou tocando nada.'
})

def is_int(s):
    try:
        int(s)
        return True
    except:
        return False

async def send_with_reaction(f, s):
    """add translation reaction to a message after sending it
    f is a message.send function
    s is a string"""
    message = await f(s)
    await message.add_reaction('❔')
