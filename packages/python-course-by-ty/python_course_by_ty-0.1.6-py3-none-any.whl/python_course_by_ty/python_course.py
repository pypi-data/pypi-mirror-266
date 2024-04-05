# The purpose of this file is to assess the answers by students taking Ty's Python course
# Students should install this code either via pip or directly placing the file in the folder they will be coding in
# The notebooks provided to the students will then import this file and make calls to it
# Each function corresponds to a quiz question in a quiz that is associated with the notebook they are working through
# If the student's answer is correct, the function will output a keyword or phrase to answer the quiz question with
# If the answer is incorrect, the function will output a statement telling them their answer was incorrect
# Risks associated with beginner python students finding answers in this file was felt to be minimal and worth alternatives

# install dependencies
import requests
from bs4 import BeautifulSoup
import re
import omdb


# Project 1 Problem 1
def test1_1(answer):
    if answer == 500000000:
        print("Tytastic")
    else:
        print("Your production_costs variable is not correct.")


def test1_2(answer):
    if answer == 1000000:
        print("Roger Roger")
    else:
        print("Your marketing_costs variable is not correct.")


def test1_3(answer):
    if answer == 1000000000:
        print("Grifftacular")
    else:
        print("Your ticket_sales variable is not correct.")


def test1_4(answer):
    if answer == 0.1:
        print("Turbo Man")
    else:
        print("Your theater_commission variable is not correct.")


def test1_5(answer):
    if answer == 399000000.0:
        print("Evil chickens")
    else:
        print("Your estimated_profits variable is not correct.")


# Project 1 Problem 2
def test1_6(answer):
    if answer == 500000:
        print("Go go gocarts")
    else:
        print("Your total_seats variable is not correct.")


def test1_7(answer):
    if answer == 13:
        print("Space monkeys")
    else:
        print("Your seat_batches variable is not correct.")


def test1_8(answer):
    if answer == 7:
        print("Dang those naughty space monkeys")
    else:
        print("Your remaining_seats variable is not correct.")


# Project 1 Problem 3
def test1_9(answer):
    if answer == 0:
        print("Manic manikin")
    else:
        print("Your kyle_production variable is not correct.")


def test1_10(answer):
    if answer == 0:
        print("Manic Monday")
    else:
        print("Your kelly_production variable is not correct.")


def test1_11(answer):
    if answer == 1:
        print("Manic monkeys")
    else:
        print("Your konner_production variable is not correct.")


def test1_12(answer):
    if answer == 4:
        print("Manic money")
    else:
        print("Your kevin_production variable is not correct.")


def test1_13(answer):
    if answer == 3:
        print("Manic munchkins")
    else:
        print("Your kassy_production variable is not correct.")


def test1_14(answer):
    if answer == 3:
        print("Manic munchies")
    else:
        print("Your kali_production variable is not correct.")


def test1_15(answer):
    if answer == 6:
        print("Manic motors")
    else:
        print("Your krissy_production variable is not correct.")


def test1_16(answer):
    if answer == 6:
        print("Manic makeup")
    else:
        print("Your kendall_production variable is not correct.")


def test1_17(answer):
    if answer == 0:
        print("Manic mill")
    else:
        print("Your kassy2_production variable is not correct.")


def test1_18(answer):
    if answer == (0.5 + 0.5 + 1 + 2):
        print("Manic mastif")
    else:
        print("Your kris_production variable is not correct.")


def test1_19(answer):
    if answer == (2 + 2 + 1 + 6):
        print("Manic moonlight")
    else:
        print("Your katelynn_production variable is not correct.")


def test1_20(answer):
    if answer == 0:
        print("Manic mayor")
    else:
        print("Your todd_production variable is not correct.")


def test1_21(answer):
    if answer == 38.0:
        print('Manic "m" words')
    else:
        print("Your total_production variable is not correct.")


# Project 1 Problem 4
def test1_22(answer):
    if answer == 1000000000:
        print("Wowzers!")
    else:
        print("Your number_of_funny_people variable does not return 1000000000")


# Project 2 Problem 1
def test2_1(answer1, answer2):
    if answer1 == 70 and answer2 == 80:
        print("Tacolicious")
    else:
        print("Your ty_luck and/or ty_skill variable(s) is/are incorrect.")


# Project 2 Problem 2
def test2_2(answer):
    if answer == "Anywhere and Anything":
        print("Chicken chapstick")
    else:
        print(
            "You're condition for a bank account with $10,000 or more in it is incorrect."
        )


def test2_3(answer):
    if answer == "Fine dining establishment and order a decent meal":
        print("Cool whip machine gun")
    else:
        print(
            "You're condition for a bank account with less than $10,000 but more than $5,000 is incorrect."
        )


def test2_4(answer):
    if answer == "Average fast food restaurant occasionally":
        print("Yabadabadoo!")
    else:
        print(
            "You're condition for what choice to make when you have $5,000 or less but more than $1,000 is incorrect."
        )


def test2_5(answer):
    if answer == "Average fast food restaurant occasionally":
        print("Jinkees!")
    else:
        print(
            "You're condition for what choice to make when you have $5,000 or less but more than $1,000 is incorrect."
        )


def test2_6(answer):
    if answer == "Average fast food restaurant occasionally":
        print("To infinity, and beyond!")
    else:
        print(
            "You're condition for what choice to make when you have $5,000 or less but more than $1,000 is incorrect."
        )


def test2_7(answer):
    if answer == "Hearty home-cooked meal at home sweet home":
        print("Tarter sauce!")
    else:
        print(
            "You're condition for what choice to make when you have $5,000 or less but more than $1,000 is incorrect."
        )


def test2_8(answer):
    if answer == "Modest meal at home":
        print("Ninja archer")
    else:
        print(
            "You're condition for what choice to make when you have $1,000 or less but more than $0 is incorrect."
        )


def test2_9(answer):
    if answer == "Meals involving primarily noodles or rice":
        print("Sumo suit scuba diving")
    else:
        print(
            "You're condition for what choice to make when you have $1,000 or less but more than $0 is incorrect."
        )


def test2_10(answer):
    if (
        answer
        == "Research how to make the stray cat that foolishly wandered into your yard last for more than 3 meals"
    ):
        print("Creative juices smoothie")
    else:
        print("You're condition for what choice to make when you have $0 is incorrect.")


# Project 2 Problem 3
def test2_11(answer):
    if answer == [
        "Ty was killed by a plunger in bouncy house by his neighbor's annoying cow",
        "Ty was killed by a plunger in bouncy house by a pack of rats sworn to conquer the human race",
        "Ty was killed by a plunger in bouncy house by that vacuum salesman Ty keeps hiding from",
        "Ty was killed by a plunger in bouncy house by that adorable puppy his kids keep asking him to buy",
        "Ty was killed by a plunger in It's A Small World Disney Land ride by his neighbor's annoying cow",
        "Ty was killed by a plunger in It's A Small World Disney Land ride by a pack of rats sworn to conquer the human race",
        "Ty was killed by a plunger in It's A Small World Disney Land ride by that vacuum salesman Ty keeps hiding from",
        "Ty was killed by a plunger in It's A Small World Disney Land ride by that adorable puppy his kids keep asking him to buy",
        "Ty was killed by a plunger in presidential oval office by his neighbor's annoying cow",
        "Ty was killed by a plunger in presidential oval office by a pack of rats sworn to conquer the human race",
        "Ty was killed by a plunger in presidential oval office by that vacuum salesman Ty keeps hiding from",
        "Ty was killed by a plunger in presidential oval office by that adorable puppy his kids keep asking him to buy",
        "Ty was killed by a plunger in South Pole-Aitken basin on the moon by his neighbor's annoying cow",
        "Ty was killed by a plunger in South Pole-Aitken basin on the moon by a pack of rats sworn to conquer the human race",
        "Ty was killed by a plunger in South Pole-Aitken basin on the moon by that vacuum salesman Ty keeps hiding from",
        "Ty was killed by a plunger in South Pole-Aitken basin on the moon by that adorable puppy his kids keep asking him to buy",
        "Ty was killed by peanuts coated in a genetically-altering substance that makes you allergic to peanuts in bouncy house by his neighbor's annoying cow",
        "Ty was killed by peanuts coated in a genetically-altering substance that makes you allergic to peanuts in bouncy house by a pack of rats sworn to conquer the human race",
        "Ty was killed by peanuts coated in a genetically-altering substance that makes you allergic to peanuts in bouncy house by that vacuum salesman Ty keeps hiding from",
        "Ty was killed by peanuts coated in a genetically-altering substance that makes you allergic to peanuts in bouncy house by that adorable puppy his kids keep asking him to buy",
        "Ty was killed by peanuts coated in a genetically-altering substance that makes you allergic to peanuts in It's A Small World Disney Land ride by his neighbor's annoying cow",
        "Ty was killed by peanuts coated in a genetically-altering substance that makes you allergic to peanuts in It's A Small World Disney Land ride by a pack of rats sworn to conquer the human race",
        "Ty was killed by peanuts coated in a genetically-altering substance that makes you allergic to peanuts in It's A Small World Disney Land ride by that vacuum salesman Ty keeps hiding from",
        "Ty was killed by peanuts coated in a genetically-altering substance that makes you allergic to peanuts in It's A Small World Disney Land ride by that adorable puppy his kids keep asking him to buy",
        "Ty was killed by peanuts coated in a genetically-altering substance that makes you allergic to peanuts in presidential oval office by his neighbor's annoying cow",
        "Ty was killed by peanuts coated in a genetically-altering substance that makes you allergic to peanuts in presidential oval office by a pack of rats sworn to conquer the human race",
        "Ty was killed by peanuts coated in a genetically-altering substance that makes you allergic to peanuts in presidential oval office by that vacuum salesman Ty keeps hiding from",
        "Ty was killed by peanuts coated in a genetically-altering substance that makes you allergic to peanuts in presidential oval office by that adorable puppy his kids keep asking him to buy",
        "Ty was killed by peanuts coated in a genetically-altering substance that makes you allergic to peanuts in South Pole-Aitken basin on the moon by his neighbor's annoying cow",
        "Ty was killed by peanuts coated in a genetically-altering substance that makes you allergic to peanuts in South Pole-Aitken basin on the moon by a pack of rats sworn to conquer the human race",
        "Ty was killed by peanuts coated in a genetically-altering substance that makes you allergic to peanuts in South Pole-Aitken basin on the moon by that vacuum salesman Ty keeps hiding from",
        "Ty was killed by peanuts coated in a genetically-altering substance that makes you allergic to peanuts in South Pole-Aitken basin on the moon by that adorable puppy his kids keep asking him to buy",
        "Ty was killed by Q-tips laced with brain-eating amoeba in bouncy house by his neighbor's annoying cow",
        "Ty was killed by Q-tips laced with brain-eating amoeba in bouncy house by a pack of rats sworn to conquer the human race",
        "Ty was killed by Q-tips laced with brain-eating amoeba in bouncy house by that vacuum salesman Ty keeps hiding from",
        "Ty was killed by Q-tips laced with brain-eating amoeba in bouncy house by that adorable puppy his kids keep asking him to buy",
        "Ty was killed by Q-tips laced with brain-eating amoeba in It's A Small World Disney Land ride by his neighbor's annoying cow",
        "Ty was killed by Q-tips laced with brain-eating amoeba in It's A Small World Disney Land ride by a pack of rats sworn to conquer the human race",
        "Ty was killed by Q-tips laced with brain-eating amoeba in It's A Small World Disney Land ride by that vacuum salesman Ty keeps hiding from",
        "Ty was killed by Q-tips laced with brain-eating amoeba in It's A Small World Disney Land ride by that adorable puppy his kids keep asking him to buy",
        "Ty was killed by Q-tips laced with brain-eating amoeba in presidential oval office by his neighbor's annoying cow",
        "Ty was killed by Q-tips laced with brain-eating amoeba in presidential oval office by a pack of rats sworn to conquer the human race",
        "Ty was killed by Q-tips laced with brain-eating amoeba in presidential oval office by that vacuum salesman Ty keeps hiding from",
        "Ty was killed by Q-tips laced with brain-eating amoeba in presidential oval office by that adorable puppy his kids keep asking him to buy",
        "Ty was killed by Q-tips laced with brain-eating amoeba in South Pole-Aitken basin on the moon by his neighbor's annoying cow",
        "Ty was killed by Q-tips laced with brain-eating amoeba in South Pole-Aitken basin on the moon by a pack of rats sworn to conquer the human race",
        "Ty was killed by Q-tips laced with brain-eating amoeba in South Pole-Aitken basin on the moon by that vacuum salesman Ty keeps hiding from",
        "Ty was killed by Q-tips laced with brain-eating amoeba in South Pole-Aitken basin on the moon by that adorable puppy his kids keep asking him to buy",
        "Ty was killed by packing peanuts in a box cut perfectly to encase Ty's rather muscular dimensions in bouncy house by his neighbor's annoying cow",
        "Ty was killed by packing peanuts in a box cut perfectly to encase Ty's rather muscular dimensions in bouncy house by a pack of rats sworn to conquer the human race",
        "Ty was killed by packing peanuts in a box cut perfectly to encase Ty's rather muscular dimensions in bouncy house by that vacuum salesman Ty keeps hiding from",
        "Ty was killed by packing peanuts in a box cut perfectly to encase Ty's rather muscular dimensions in bouncy house by that adorable puppy his kids keep asking him to buy",
        "Ty was killed by packing peanuts in a box cut perfectly to encase Ty's rather muscular dimensions in It's A Small World Disney Land ride by his neighbor's annoying cow",
        "Ty was killed by packing peanuts in a box cut perfectly to encase Ty's rather muscular dimensions in It's A Small World Disney Land ride by a pack of rats sworn to conquer the human race",
        "Ty was killed by packing peanuts in a box cut perfectly to encase Ty's rather muscular dimensions in It's A Small World Disney Land ride by that vacuum salesman Ty keeps hiding from",
        "Ty was killed by packing peanuts in a box cut perfectly to encase Ty's rather muscular dimensions in It's A Small World Disney Land ride by that adorable puppy his kids keep asking him to buy",
        "Ty was killed by packing peanuts in a box cut perfectly to encase Ty's rather muscular dimensions in presidential oval office by his neighbor's annoying cow",
        "Ty was killed by packing peanuts in a box cut perfectly to encase Ty's rather muscular dimensions in presidential oval office by a pack of rats sworn to conquer the human race",
        "Ty was killed by packing peanuts in a box cut perfectly to encase Ty's rather muscular dimensions in presidential oval office by that vacuum salesman Ty keeps hiding from",
        "Ty was killed by packing peanuts in a box cut perfectly to encase Ty's rather muscular dimensions in presidential oval office by that adorable puppy his kids keep asking him to buy",
        "Ty was killed by packing peanuts in a box cut perfectly to encase Ty's rather muscular dimensions in South Pole-Aitken basin on the moon by his neighbor's annoying cow",
        "Ty was killed by packing peanuts in a box cut perfectly to encase Ty's rather muscular dimensions in South Pole-Aitken basin on the moon by a pack of rats sworn to conquer the human race",
        "Ty was killed by packing peanuts in a box cut perfectly to encase Ty's rather muscular dimensions in South Pole-Aitken basin on the moon by that vacuum salesman Ty keeps hiding from",
        "Ty was killed by packing peanuts in a box cut perfectly to encase Ty's rather muscular dimensions in South Pole-Aitken basin on the moon by that adorable puppy his kids keep asking him to buy",
    ]:
        print("Didgeridoo")
    else:
        print("Your implementation of the loops or list append is not correct.")


def test2_12(answer, noun, verb, adjective):
    noun = noun
    verb = verb
    adjective = adjective
    story_test = (
        "Ty stood in his laboratory, staring at the "
        + noun
        + ". After a long sigh, he wiped his "
        + adjective
        + " forehead and took a long drink from his jar of pickle juice (he "
        + verb
        + " pickle juice at times like these). Well, the "
        + noun
        + " wasn't going to just disappear along with all his problems. Ty counted down, '3, 2...1 and a half....1 and a quarter.....' This wasn't going to be "
        + adjective
        + ". Ty began trying to calculate the smallest fractions by which he could count. Suddenly the "
        + noun
        + " "
        + verb
        + ". Ty hastily reached down at the "
        + noun
        + " with one hand to "
        + verb
        + " the "
        + noun
        + " and brought a syringe secretly and slowly around with the other, adrenaline "
        + verb
        + " through his veins. The "
        + noun
        + " struck out in a "
        + adjective
        + " rage. Ty's mother was right, he should have just become a data analyst instead. The "
        + noun
        + " "
        + verb
        + " Ty again, then again, then another time. Ty's thoughts were quickly becoming incoherent. But while the "
        + noun
        + " was distracted with all its "
        + adjective
        + " "
        + verb
        + " (which felt very non-"
        + adjective
        + " to Ty), Ty snuck the syringe around and thrust it at the "
        + noun
        + "'s side, and right into his own arm. Ty REALLY should have just become a data analyst."
    )
    if answer == story_test:
        print("Snozzberries")
    else:
        print(story_test)
        print("You did not create the mad_libs function correctly.")


# Project 3 Problem 1
def test3_1(answer):
    if answer == [
        "\ufeffDad Jokes",
        "",
        "",
        "What do you call a fish with no eyes? Fsh.",
        "What should you do if you meet a giant? Use big words.",
        "What do you call a cow with two legs? Lean beef.",
        "What sits on the seabed and has anxiety? A nervous wreck.",
        "What do you call a man wearing a rug on his head? Matt.",
        "What’s the best air to breathe if you want to be rich? Millionaire.",
        "Why did the girl toss a clock out the window? She wanted to see time fly.",
        "Where do armies belong? In your sleeves.",
        "What did one plate say to another plate? Tonight, dinner's on me.",
        "Did you hear about the king that went to the dentist? He needed to get crowns.",
        "What happens when doctors get frustrated? They lose their patients.",
        "What do you call a bear with no teeth? A gummy bear.",
        "What invention allows us to see through walls? Windows.",
        "What’s orange and sounds like a parrot? A carrot.",
        "Why did the coach go to the bank? To get his quarter back.",
        "Why do nurses like red crayons? Sometimes they have to draw blood.",
        "What kind of jewelry do rabbits wear? 14 carrot gold.",
        "Why can't the sailor learn the alphabet? Because he kept getting lost at C.",
        "What do you call a cheese that isn’t yours? Nacho cheese!",
        "How do celebrities keep cool? They have many fans.",
        "What did the janitor say when he jumped out of the closet? Supplies!",
        "Why did the boy bring a ladder on the bus? He wanted to go to high school.",
        "Why did the golfer bring two pairs of pants? Just in case he got a hole in one.",
        "Why did the cowboy adopt a wiener dog? He wanted to get a long little doggie.",
        "How did the barber win the race? He knew a shortcut.",
        "What’s more unbelievable than a talking dog? A spelling bee.",
        "What do you call a cow with no legs? Ground beef.",
        "What do you call a happy cowboy? A jolly rancher.",
        "Why shouldn’t you trust trees? They seem shady.",
        "How do you fix a broken tomato? With tomato paste.",
        "What kind of music scares balloons? Pop music.",
        "Why did the orange stop halfway across the road? It ran out of juice.",
        "Why did the Oreo go to the dentist? It lost its filling.",
        "How do you get an astronaut’s baby to stop crying? You rocket.",
        "What do dogs and phones have in common? Both have collar ID.",
        "Why shouldn't you play poker in the jungle? Too many cheetahs.",
        "What sounds like a sneeze and is made of leather? A shoe.",
        "How do you stop a bull from charging? You cancel its credit card.",
        "Why was the math book sad? It had too many problems.",
        "Why are fish so smart? Because they swim in schools.",
        "Why did the employee get fired from the keyboard factory? He wasn’t putting in enough shifts.",
        "Did you hear about the man who cut off his left leg? He’s all right now.",
        "Did you hear the one about the claustrophobic astronaut? He just needed a little space.",
        "What kind of music should you listen to while fishing? Something catchy!",
        "What do you call a girl in the middle of a tennis court? Annette.",
        "What did the ocean say to the beach? Nothing. It just waved.",
        "What did one wall say to the other? I’ll meet you at the corner.",
        "Why did the nose feel sad? It was always getting picked on.",
        "Did you hear about the cold dinner? It was chili.",
        "Why did the deer go to the dentist? It had buck teeth.",
        "Why can’t you trust a balloon? It’s full of hot air",
        "A cheese factory exploded in France. Da brie is everywhere!",
        "Not sure if you have noticed, but I love bad puns. That’s just how eye roll.",
        "Why did the banana go to the doctor? Because it wasn’t peeling well.",
        "Where does a sheep go to get a haircut? The baa baa shop.",
        "What did the mama cow say to the baby cow? It’s pasture bed time.",
        "Why should you never use a dull pencil? Because it’s pointless.",
        "Why did the cookie go to the doctor? It was feeling crumby.",
        "Where did the cat go after losing its tail? The retail store.",
        "Why don’t eggs tell jokes? They’d crack each other up.",
        "What kind of sandals do frogs wear? Open-toad.",
        "What do you call a herd of sheep falling down a hill? A lambslide.",
        "How do you organize a space party? You planet.",
        "How many tickles does it take to make an octopus laugh? Ten tickles.",
        "What do you call a potato wearing glasses? A spec-tater.",
        "What do you call a moose with no name? Anonymoose.",
        "Why did the ram run over the cliff? He didn’t see the ewe turn.",
        "Why did the picture go to jail? He was framed.",
        "What is a calendar’s favorite food? Dates.",
        "Why was the football stadium cold? There were too many fans.",
        "Why do bananas wear sunscreen? Because they peel.",
        "Why do bees have sticky hair? Because they use honey combs.",
        "Why did the watch go on vacation? To unwind.",
        "How does a penguin build a house? Igloos it together.",
        "Why do melons have weddings? Because they cantaloupe.",
        "Why did the computer get glasses? To improve its website.",
        "What did the blanket say to the bed? I’ve got you covered.",
        "What did the roof say to the shingle? The first one’s on the house.",
        "What do you call birds that stick together? Velcrows",
        "Why did the duck fall on the sidewalk? He tripped on a quack.",
        "How do birds learn to fly? They wing it.",
        "Did you hear about the walnut and cashew that threw a party? It was nuts.",
        "Did the hear about the ice cream truck accident? It crashed on a rocky road.",
        "What kind of bird works on a construction site? A crane.",
        "What did one elevator say to the other elevator? I think I’m coming down with something.",
        "What did the hamburger name its baby? Patty.",
        "What type of music do the planets enjoy? Neptunes.",
        "Why did the phone wear glasses? Because it lost all its contacts.",
        "Why do bakers work so hard? Because they knead dough.",
        "Why are fish so easy to weigh? Because they have their own set of scales.",
        "What do you call a priest that becomes a lawyer? A father-in-law.",
        "What do you give a scientist with bad breath? Experi-mints.",
        "What did Benjamin Franklin say when he discovered electricity? Nothing. He was too shocked.",
        "What do you call a medieval lamp? A knight light.",
        "What did one hat say to the other? You go on ahead.",
        "Why did the frog take the bus to work? His car got toad.",
        "What does an evil hen lay? Deviled eggs.",
        "How can you tell the difference between a dog and tree? By their bark.",
        "Why do dragons sleep during the day? Because they like to fight knights.",
        "Why did the scarecrow win an award? It was outstanding in its field.",
        "Did you hear about the 12-inch dog? It was a foot long.",
        "Why did the baseball player get arrested? He stole third base.",
        "What did one piece of tape say to the other? Let’s stick together.",
        "What's brown and sticky? A stick.",
        "How does the rancher keep track of his cattle? With a cow-culator.",
        "What do you call a shoe made out of a banana? A slipper.",
        "How you fix a broken pumpkin? With a pumpkin patch.",
        "Where do boats go when they’re sick? To the dock.",
        "Can February March? No, but April May!",
        "What do you call a fibbing cat? A lion.",
        "Did you hear the rumor about butter? Well, I’m not going to go spreading it!",
        "Where do you learn to make ice cream? Sundae school.",
        "What’s a scarecrow’s favorite fruit? Straw-berries",
        "Where do burgers go dancing? At the meatball.",
        "What time do ducks wake up? At the quack of dawn.",
        "Why was the broom late? It over-swept.",
        "What kind of tree fits in your hand? A palm tree.",
        "Where do books hide when they’re afraid? Under their covers.",
        "How do trees get on the internet? They log in.",
        "What does a painter do when he gets cold? Puts on another coat.",
        "What did the calculator say to the pencil? You can count on me.",
        "What has four wheels and flies? A garbage truck.",
        "What do you call two ducks and a cow? Quackers and milk.",
        "What do cows like to read? Cattle-logs.",
        "How did the farmer fix his torn overalls? With a cabbage patch.",
        "How much money does a skunk have? Just one scent.",
        "What do you get when you cross an elephant and a fish? Swimming trunks.",
        "What kind of cereal do leprechauns eat? Lucky Charms.",
        "What do you call recently-married spiders? Newly-webs.",
        "Where do crayons go on vacation? Color-ado.",
        "What do you get when you cross a Smurf and a cow? Blue cheese.",
        "What happens when ice cream gets angry? It has a meltdown.",
        "What do you call a locomotive carrying bubble gum? A chew chew train.",
        "How do you get a mouse to smile? Say “cheese.”",
        "Why couldn’t the bike stand up on its own? It was too tired.",
        "What do you call a sheep that knows karate? A lamb chop.",
        "Why did the snowman buy a bag of carrots? He wanted to pick his nose.",
        "What did the Dalmatian say after dinner? That hit the spot.",
        "How do you know when a bike is thinking? You can see its wheels turning.",
        "What does a librarian use to go fishing? A bookworm.",
        "What did one leaf say to the other? I’m falling for you.",
        "Where’s the one place you should never take your dog? A flea market.",
        "How does Darth Vader like his bagels? On the dark side.",
        "What do you call spaghetti in disguise? An impasta.",
        "Why did the tailor get fired? He wasn’t a good fit.",
        "Where do elephants store luggage? In a trunk.",
        "Why did the poodle buy a clock? It wanted to be a watch dog.",
        "Why do birds fly south? Because it’s too far to talk.",
        "What do you call a fly with a sore throat? A hoarse fly.",
        "Dogs can’t operate MRI machines — but cats-can.",
        "If you see a robbery at an Apple store, does that make you an iWitness?",
        "I had a date last night. It was perfect. Tomorrow, I’ll have a grape.",
        "Justice is a dish best served cold. If it were served warm, it would be just-water.",
        "It was an emotional wedding — even the cake was in tiers.",
        "Why did Waldo go to therapy? To find himself.",
        "I have an inferiority complex, but it’s not a very good one.",
        "Our vacuum cleaner is getting old. It's just gathering dust.",
        "Why did the thief take a shower before robbing the bank? He wanted to make a clean getaway.",
        "What do lawyers wear to work? Law suits.",
        "Why was the traffic light late to work? It took too long to change.",
        "Why do hamburgers go south for the winter? So they don’t freeze their buns.",
        "Why didn’t the sun go to college? It already had a million degrees.",
        "What do you call someone who can’t stick to a diet? A desserter.",
        "Why did the little strawberry cry? His mom was in a jam.",
        "Why couldn’t the toilet paper cross the road? It got stuck in a crack.",
        "What do you get from a pampered cow? Spoiled milk.",
        "Why did the whale blush? It saw the ocean’s bottom.",
        "Getting paid to sleep would be my dream job.",
        "I used to be a banker, but I lost interest.",
        "Why can’t you trust an atom? Because they make up everything.",
        "I went to buy a pair of camouflage pants, but I couldn’t find any.",
        "Why did the tomato blush? It saw the salad dressing.",
        "I haven’t talked to my wife in a week — I didn’t want to interrupt her.",
        "Why are pigs bad drivers? They hog the road.",
        "I’m so good at sleeping, I can do it with my eyes closed!",
        "Why did police arrest the turkey? They suspected fowl play.",
        "What do computers eat for a snack? Microchips.",
        "How do frogs invest their money? They use a stock croaker.",
        "Did you hear about the whale that swallowed a clown? It felt funny after.",
        "The past, present and future walked into a bar. It was tense.",
    ]:
        print("Monty Python")
    else:
        print("Your dad_jokes list is not correct.")


# Project 3 Problem 2
def test3_2(answer):
    if answer == "What do you call a man wearing a rug on his head? Matt.":
        print("Pickle suckers")
    else:
        print("Your function returns the wrong line for integer 8.")


def test3_3(answer):
    if answer == "What kind of jewelry do rabbits wear? 14 carrot gold.":
        print("Self-cleaning toilets, it's going to be big")
    else:
        print("Your function returns the wrong line for integer 20")


def test3_4(answer):
    if answer == "\ufeffDad Jokes":
        print("Nokia brick phones")
    else:
        print("Your function returns the wrong line for integer 1.")


# Project 3 Problem 3
def test3_5(answer):
    if answer == [
        "What do you call a fish with no eyes? Fsh.",
        "What should you do if you meet a giant? Use big words.",
        "What do you call a cow with two legs? Lean beef.",
        "What sits on the seabed and has anxiety? A nervous wreck.",
        "What do you call a man wearing a rug on his head? Matt.",
        "What’s the best air to breathe if you want to be rich? Millionaire.",
        "Why did the girl toss a clock out the window? She wanted to see time fly.",
        "Where do armies belong? In your sleeves.",
        "What did one plate say to another plate? Tonight, dinner's on me.",
        "Did you hear about the king that went to the dentist? He needed to get crowns.",
        "What happens when doctors get frustrated? They lose their patients.",
        "What do you call a bear with no teeth? A gummy bear.",
        "What invention allows us to see through walls? Windows.",
        "What’s orange and sounds like a parrot? A carrot.",
        "Why did the coach go to the bank? To get his quarter back.",
        "Why do nurses like red crayons? Sometimes they have to draw blood.",
        "What kind of jewelry do rabbits wear? 14 carrot gold.",
        "Why can't the sailor learn the alphabet? Because he kept getting lost at C.",
        "What do you call a cheese that isn’t yours? Nacho cheese!",
        "How do celebrities keep cool? They have many fans.",
        "What did the janitor say when he jumped out of the closet? Supplies!",
        "Why did the boy bring a ladder on the bus? He wanted to go to high school.",
        "Why did the golfer bring two pairs of pants? Just in case he got a hole in one.",
        "Why did the cowboy adopt a wiener dog? He wanted to get a long little doggie.",
        "How did the barber win the race? He knew a shortcut.",
        "What’s more unbelievable than a talking dog? A spelling bee.",
        "What do you call a cow with no legs? Ground beef.",
        "What do you call a happy cowboy? A jolly rancher.",
        "Why shouldn’t you trust trees? They seem shady.",
        "How do you fix a broken tomato? With tomato paste.",
        "What kind of music scares balloons? Pop music.",
        "Why did the orange stop halfway across the road? It ran out of juice.",
        "Why did the Oreo go to the dentist? It lost its filling.",
        "How do you get an astronaut’s baby to stop crying? You rocket.",
        "What do dogs and phones have in common? Both have collar ID.",
        "Why shouldn't you play poker in the jungle? Too many cheetahs.",
        "What sounds like a sneeze and is made of leather? A shoe.",
        "How do you stop a bull from charging? You cancel its credit card.",
        "Why was the math book sad? It had too many problems.",
        "Why are fish so smart? Because they swim in schools.",
        "Why did the employee get fired from the keyboard factory? He wasn’t putting in enough shifts.",
        "Did you hear about the man who cut off his left leg? He’s all right now.",
        "Did you hear the one about the claustrophobic astronaut? He just needed a little space.",
        "What kind of music should you listen to while fishing? Something catchy!",
        "What do you call a girl in the middle of a tennis court? Annette.",
        "What did the ocean say to the beach? Nothing. It just waved.",
        "What did one wall say to the other? I’ll meet you at the corner.",
        "Why did the nose feel sad? It was always getting picked on.",
        "Did you hear about the cold dinner? It was chili.",
        "Why did the deer go to the dentist? It had buck teeth.",
        "Why can’t you trust a balloon? It’s full of hot air",
        "A cheese factory exploded in France. Da brie is everywhere!",
        "Not sure if you have noticed, but I love bad puns. That’s just how eye roll.",
        "Why did the banana go to the doctor? Because it wasn’t peeling well.",
        "Where does a sheep go to get a haircut? The baa baa shop.",
        "What did the mama cow say to the baby cow? It’s pasture bed time.",
        "Why should you never use a dull pencil? Because it’s pointless.",
        "Why did the cookie go to the doctor? It was feeling crumby.",
        "Where did the cat go after losing its tail? The retail store.",
        "Why don’t eggs tell jokes? They’d crack each other up.",
        "What kind of sandals do frogs wear? Open-toad.",
        "What do you call a herd of sheep falling down a hill? A lambslide.",
        "How do you organize a space party? You planet.",
        "How many tickles does it take to make an octopus laugh? Ten tickles.",
        "What do you call a potato wearing glasses? A spec-tater.",
        "What do you call a moose with no name? Anonymoose.",
        "Why did the ram run over the cliff? He didn’t see the ewe turn.",
        "Why did the picture go to jail? He was framed.",
        "What is a calendar’s favorite food? Dates.",
        "Why was the football stadium cold? There were too many fans.",
        "Why do bananas wear sunscreen? Because they peel.",
        "Why do bees have sticky hair? Because they use honey combs.",
        "Why did the watch go on vacation? To unwind.",
        "How does a penguin build a house? Igloos it together.",
        "Why do melons have weddings? Because they cantaloupe.",
        "Why did the computer get glasses? To improve its website.",
        "What did the blanket say to the bed? I’ve got you covered.",
        "What did the roof say to the shingle? The first one’s on the house.",
        "What do you call birds that stick together? Velcrows",
        "Why did the duck fall on the sidewalk? He tripped on a quack.",
        "How do birds learn to fly? They wing it.",
        "Did you hear about the walnut and cashew that threw a party? It was nuts.",
        "Did the hear about the ice cream truck accident? It crashed on a rocky road.",
        "What kind of bird works on a construction site? A crane.",
        "What did one elevator say to the other elevator? I think I’m coming down with something.",
        "What did the hamburger name its baby? Patty.",
        "What type of music do the planets enjoy? Neptunes.",
        "Why did the phone wear glasses? Because it lost all its contacts.",
        "Why do bakers work so hard? Because they knead dough.",
        "Why are fish so easy to weigh? Because they have their own set of scales.",
        "What do you call a priest that becomes a lawyer? A father-in-law.",
        "What do you give a scientist with bad breath? Experi-mints.",
        "What did Benjamin Franklin say when he discovered electricity? Nothing. He was too shocked.",
        "What do you call a medieval lamp? A knight light.",
        "What did one hat say to the other? You go on ahead.",
        "Why did the frog take the bus to work? His car got toad.",
        "What does an evil hen lay? Deviled eggs.",
        "How can you tell the difference between a dog and tree? By their bark.",
        "Why do dragons sleep during the day? Because they like to fight knights.",
        "Why did the scarecrow win an award? It was outstanding in its field.",
        "Did you hear about the 12-inch dog? It was a foot long.",
        "Why did the baseball player get arrested? He stole third base.",
        "What did one piece of tape say to the other? Let’s stick together.",
        "What's brown and sticky? A stick.",
        "How does the rancher keep track of his cattle? With a cow-culator.",
        "What do you call a shoe made out of a banana? A slipper.",
        "How you fix a broken pumpkin? With a pumpkin patch.",
        "Where do boats go when they’re sick? To the dock.",
        "Can February March? No, but April May!",
        "What do you call a fibbing cat? A lion.",
        "Did you hear the rumor about butter? Well, I’m not going to go spreading it!",
        "Where do you learn to make ice cream? Sundae school.",
        "What’s a scarecrow’s favorite fruit? Straw-berries",
        "Where do burgers go dancing? At the meatball.",
        "What time do ducks wake up? At the quack of dawn.",
        "Why was the broom late? It over-swept.",
        "What kind of tree fits in your hand? A palm tree.",
        "Where do books hide when they’re afraid? Under their covers.",
        "How do trees get on the internet? They log in.",
        "What does a painter do when he gets cold? Puts on another coat.",
        "What did the calculator say to the pencil? You can count on me.",
        "What has four wheels and flies? A garbage truck.",
        "What do you call two ducks and a cow? Quackers and milk.",
        "What do cows like to read? Cattle-logs.",
        "How did the farmer fix his torn overalls? With a cabbage patch.",
        "How much money does a skunk have? Just one scent.",
        "What do you get when you cross an elephant and a fish? Swimming trunks.",
        "What kind of cereal do leprechauns eat? Lucky Charms.",
        "What do you call recently-married spiders? Newly-webs.",
        "Where do crayons go on vacation? Color-ado.",
        "What do you get when you cross a Smurf and a cow? Blue cheese.",
        "What happens when ice cream gets angry? It has a meltdown.",
        "What do you call a locomotive carrying bubble gum? A chew chew train.",
        "How do you get a mouse to smile? Say “cheese.”",
        "Why couldn’t the bike stand up on its own? It was too tired.",
        "What do you call a sheep that knows karate? A lamb chop.",
        "Why did the snowman buy a bag of carrots? He wanted to pick his nose.",
        "What did the Dalmatian say after dinner? That hit the spot.",
        "How do you know when a bike is thinking? You can see its wheels turning.",
        "What does a librarian use to go fishing? A bookworm.",
        "What did one leaf say to the other? I’m falling for you.",
        "Where’s the one place you should never take your dog? A flea market.",
        "How does Darth Vader like his bagels? On the dark side.",
        "What do you call spaghetti in disguise? An impasta.",
        "Why did the tailor get fired? He wasn’t a good fit.",
        "Where do elephants store luggage? In a trunk.",
        "Why did the poodle buy a clock? It wanted to be a watch dog.",
        "Why do birds fly south? Because it’s too far to talk.",
        "What do you call a fly with a sore throat? A hoarse fly.",
        "Dogs can’t operate MRI machines — but cats-can.",
        "If you see a robbery at an Apple store, does that make you an iWitness?",
        "I had a date last night. It was perfect. Tomorrow, I’ll have a grape.",
        "Justice is a dish best served cold. If it were served warm, it would be just-water.",
        "It was an emotional wedding — even the cake was in tiers.",
        "Why did Waldo go to therapy? To find himself.",
        "I have an inferiority complex, but it’s not a very good one.",
        "Our vacuum cleaner is getting old. It's just gathering dust.",
        "Why did the thief take a shower before robbing the bank? He wanted to make a clean getaway.",
        "What do lawyers wear to work? Law suits.",
        "Why was the traffic light late to work? It took too long to change.",
        "Why do hamburgers go south for the winter? So they don’t freeze their buns.",
        "Why didn’t the sun go to college? It already had a million degrees.",
        "What do you call someone who can’t stick to a diet? A desserter.",
        "Why did the little strawberry cry? His mom was in a jam.",
        "Why couldn’t the toilet paper cross the road? It got stuck in a crack.",
        "What do you get from a pampered cow? Spoiled milk.",
        "Why did the whale blush? It saw the ocean’s bottom.",
        "Getting paid to sleep would be my dream job.",
        "I used to be a banker, but I lost interest.",
        "Why can’t you trust an atom? Because they make up everything.",
        "I went to buy a pair of camouflage pants, but I couldn’t find any.",
        "Why did the tomato blush? It saw the salad dressing.",
        "I haven’t talked to my wife in a week — I didn’t want to interrupt her.",
        "Why are pigs bad drivers? They hog the road.",
        "I’m so good at sleeping, I can do it with my eyes closed!",
        "Why did police arrest the turkey? They suspected fowl play.",
        "What do computers eat for a snack? Microchips.",
        "How do frogs invest their money? They use a stock croaker.",
        "Did you hear about the whale that swallowed a clown? It felt funny after.",
        "The past, present and future walked into a bar. It was tense.",
    ]:
        print("Two roads diverged")
    else:
        print("Your jokes list is incorrect.")


def test3_6(answer):
    if (
        answer
        == "What do you call a fish with no eyes? Fsh. What should you do if you meet a giant? Use big words. What do you call a cow with two legs? Lean beef. What sits on the seabed and has anxiety? A nervous wreck. What do you call a man wearing a rug on his head? Matt. What’s the best air to breathe if you want to be rich? Millionaire. Why did the girl toss a clock out the window? She wanted to see time fly. Where do armies belong? In your sleeves. What did one plate say to another plate? Tonight, dinner's on me. Did you hear about the king that went to the dentist? He needed to get crowns. What happens when doctors get frustrated? They lose their patients. What do you call a bear with no teeth? A gummy bear. What invention allows us to see through walls? Windows. What’s orange and sounds like a parrot? A carrot. Why did the coach go to the bank? To get his quarter back. Why do nurses like red crayons? Sometimes they have to draw blood. What kind of jewelry do rabbits wear? 14 carrot gold. Why can't the sailor learn the alphabet? Because he kept getting lost at C. What do you call a cheese that isn’t yours? Nacho cheese! How do celebrities keep cool? They have many fans. What did the janitor say when he jumped out of the closet? Supplies! Why did the boy bring a ladder on the bus? He wanted to go to high school. Why did the golfer bring two pairs of pants? Just in case he got a hole in one. Why did the cowboy adopt a wiener dog? He wanted to get a long little doggie. How did the barber win the race? He knew a shortcut. What’s more unbelievable than a talking dog? A spelling bee. What do you call a cow with no legs? Ground beef. What do you call a happy cowboy? A jolly rancher. Why shouldn’t you trust trees? They seem shady. How do you fix a broken tomato? With tomato paste. What kind of music scares balloons? Pop music. Why did the orange stop halfway across the road? It ran out of juice. Why did the Oreo go to the dentist? It lost its filling. How do you get an astronaut’s baby to stop crying? You rocket. What do dogs and phones have in common? Both have collar ID. Why shouldn't you play poker in the jungle? Too many cheetahs. What sounds like a sneeze and is made of leather? A shoe. How do you stop a bull from charging? You cancel its credit card. Why was the math book sad? It had too many problems. Why are fish so smart? Because they swim in schools. Why did the employee get fired from the keyboard factory? He wasn’t putting in enough shifts. Did you hear about the man who cut off his left leg? He’s all right now. Did you hear the one about the claustrophobic astronaut? He just needed a little space. What kind of music should you listen to while fishing? Something catchy! What do you call a girl in the middle of a tennis court? Annette. What did the ocean say to the beach? Nothing. It just waved. What did one wall say to the other? I’ll meet you at the corner. Why did the nose feel sad? It was always getting picked on. Did you hear about the cold dinner? It was chili. Why did the deer go to the dentist? It had buck teeth. Why can’t you trust a balloon? It’s full of hot air A cheese factory exploded in France. Da brie is everywhere! Not sure if you have noticed, but I love bad puns. That’s just how eye roll. Why did the banana go to the doctor? Because it wasn’t peeling well. Where does a sheep go to get a haircut? The baa baa shop. What did the mama cow say to the baby cow? It’s pasture bed time. Why should you never use a dull pencil? Because it’s pointless. Why did the cookie go to the doctor? It was feeling crumby. Where did the cat go after losing its tail? The retail store. Why don’t eggs tell jokes? They’d crack each other up. What kind of sandals do frogs wear? Open-toad. What do you call a herd of sheep falling down a hill? A lambslide. How do you organize a space party? You planet. How many tickles does it take to make an octopus laugh? Ten tickles. What do you call a potato wearing glasses? A spec-tater. What do you call a moose with no name? Anonymoose. Why did the ram run over the cliff? He didn’t see the ewe turn. Why did the picture go to jail? He was framed. What is a calendar’s favorite food? Dates. Why was the football stadium cold? There were too many fans. Why do bananas wear sunscreen? Because they peel. Why do bees have sticky hair? Because they use honey combs. Why did the watch go on vacation? To unwind. How does a penguin build a house? Igloos it together. Why do melons have weddings? Because they cantaloupe. Why did the computer get glasses? To improve its website. What did the blanket say to the bed? I’ve got you covered. What did the roof say to the shingle? The first one’s on the house. What do you call birds that stick together? Velcrows Why did the duck fall on the sidewalk? He tripped on a quack. How do birds learn to fly? They wing it. Did you hear about the walnut and cashew that threw a party? It was nuts. Did the hear about the ice cream truck accident? It crashed on a rocky road. What kind of bird works on a construction site? A crane. What did one elevator say to the other elevator? I think I’m coming down with something. What did the hamburger name its baby? Patty. What type of music do the planets enjoy? Neptunes. Why did the phone wear glasses? Because it lost all its contacts. Why do bakers work so hard? Because they knead dough. Why are fish so easy to weigh? Because they have their own set of scales. What do you call a priest that becomes a lawyer? A father-in-law. What do you give a scientist with bad breath? Experi-mints. What did Benjamin Franklin say when he discovered electricity? Nothing. He was too shocked. What do you call a medieval lamp? A knight light. What did one hat say to the other? You go on ahead. Why did the frog take the bus to work? His car got toad. What does an evil hen lay? Deviled eggs. How can you tell the difference between a dog and tree? By their bark. Why do dragons sleep during the day? Because they like to fight knights. Why did the scarecrow win an award? It was outstanding in its field. Did you hear about the 12-inch dog? It was a foot long. Why did the baseball player get arrested? He stole third base. What did one piece of tape say to the other? Let’s stick together. What's brown and sticky? A stick. How does the rancher keep track of his cattle? With a cow-culator. What do you call a shoe made out of a banana? A slipper. How you fix a broken pumpkin? With a pumpkin patch. Where do boats go when they’re sick? To the dock. Can February March? No, but April May! What do you call a fibbing cat? A lion. Did you hear the rumor about butter? Well, I’m not going to go spreading it! Where do you learn to make ice cream? Sundae school. What’s a scarecrow’s favorite fruit? Straw-berries Where do burgers go dancing? At the meatball. What time do ducks wake up? At the quack of dawn. Why was the broom late? It over-swept. What kind of tree fits in your hand? A palm tree. Where do books hide when they’re afraid? Under their covers. How do trees get on the internet? They log in. What does a painter do when he gets cold? Puts on another coat. What did the calculator say to the pencil? You can count on me. What has four wheels and flies? A garbage truck. What do you call two ducks and a cow? Quackers and milk. What do cows like to read? Cattle-logs. How did the farmer fix his torn overalls? With a cabbage patch. How much money does a skunk have? Just one scent. What do you get when you cross an elephant and a fish? Swimming trunks. What kind of cereal do leprechauns eat? Lucky Charms. What do you call recently-married spiders? Newly-webs. Where do crayons go on vacation? Color-ado. What do you get when you cross a Smurf and a cow? Blue cheese. What happens when ice cream gets angry? It has a meltdown. What do you call a locomotive carrying bubble gum? A chew chew train. How do you get a mouse to smile? Say “cheese.” Why couldn’t the bike stand up on its own? It was too tired. What do you call a sheep that knows karate? A lamb chop. Why did the snowman buy a bag of carrots? He wanted to pick his nose. What did the Dalmatian say after dinner? That hit the spot. How do you know when a bike is thinking? You can see its wheels turning. What does a librarian use to go fishing? A bookworm. What did one leaf say to the other? I’m falling for you. Where’s the one place you should never take your dog? A flea market. How does Darth Vader like his bagels? On the dark side. What do you call spaghetti in disguise? An impasta. Why did the tailor get fired? He wasn’t a good fit. Where do elephants store luggage? In a trunk. Why did the poodle buy a clock? It wanted to be a watch dog. Why do birds fly south? Because it’s too far to talk. What do you call a fly with a sore throat? A hoarse fly. Dogs can’t operate MRI machines — but cats-can. If you see a robbery at an Apple store, does that make you an iWitness? I had a date last night. It was perfect. Tomorrow, I’ll have a grape. Justice is a dish best served cold. If it were served warm, it would be just-water. It was an emotional wedding — even the cake was in tiers. Why did Waldo go to therapy? To find himself. I have an inferiority complex, but it’s not a very good one. Our vacuum cleaner is getting old. It's just gathering dust. Why did the thief take a shower before robbing the bank? He wanted to make a clean getaway. What do lawyers wear to work? Law suits. Why was the traffic light late to work? It took too long to change. Why do hamburgers go south for the winter? So they don’t freeze their buns. Why didn’t the sun go to college? It already had a million degrees. What do you call someone who can’t stick to a diet? A desserter. Why did the little strawberry cry? His mom was in a jam. Why couldn’t the toilet paper cross the road? It got stuck in a crack. What do you get from a pampered cow? Spoiled milk. Why did the whale blush? It saw the ocean’s bottom. Getting paid to sleep would be my dream job. I used to be a banker, but I lost interest. Why can’t you trust an atom? Because they make up everything. I went to buy a pair of camouflage pants, but I couldn’t find any. Why did the tomato blush? It saw the salad dressing. I haven’t talked to my wife in a week — I didn’t want to interrupt her. Why are pigs bad drivers? They hog the road. I’m so good at sleeping, I can do it with my eyes closed! Why did police arrest the turkey? They suspected fowl play. What do computers eat for a snack? Microchips. How do frogs invest their money? They use a stock croaker. Did you hear about the whale that swallowed a clown? It felt funny after. The past, present and future walked into a bar. It was tense. "
    ):
        print("Rikki-tikky-tavi")
    else:
        print("Your all_jokes variable is incorrect.")


# Project 3 Problem 4
def test3_7(answer):
    if (
        answer
        == "What do you call a fish with no eyes? Fsh. What should you do if you meet a giant? Use big words. What do you call a  with two legs? Lean beef. What sits on the seabed and has anxiety? A nervous wreck. What do you call a man wearing a rug on his head? Matt. What’s the best air to breathe if you want to be rich? Millionaire. Why did the girl toss a clock out the window? She wanted to see time fly. Where do armies belong? In your sleeves. What did one plate say to another plate? Tonight, dinner's on me. Did you hear about the king that went to the dentist? He needed to get crowns. What happens when doctors get frustrated? They lose their patients. What do you call a bear with no teeth? A gummy bear. What invention allows us to see through walls? Windows. What’s orange and sounds like a parrot? A carrot. Why did the coach go to the bank? To get his quarter back. Why do nurses like red crayons? Sometimes they have to draw blood. What kind of jewelry do rabbits wear? 14 carrot gold. Why can't the sailor learn the alphabet? Because he kept getting lost at C. What do you call a cheese that isn’t yours? Nacho cheese! How do celebrities keep cool? They have many fans. What did the janitor say when he jumped out of the closet? Supplies! Why did the boy bring a ladder on the bus? He wanted to go to high school. Why did the golfer bring two pairs of pants? Just in case he got a hole in one. Why did the boy adopt a wiener dog? He wanted to get a long little doggie. How did the barber win the race? He knew a shortcut. What’s more unbelievable than a talking dog? A spelling bee. What do you call a  with no legs? Ground beef. What do you call a happy boy? A jolly rancher. Why shouldn’t you trust trees? They seem shady. How do you fix a broken tomato? With tomato paste. What kind of music scares balloons? Pop music. Why did the orange stop halfway across the road? It ran out of juice. Why did the Oreo go to the dentist? It lost its filling. How do you get an astronaut’s baby to stop crying? You rocket. What do dogs and phones have in common? Both have collar ID. Why shouldn't you play poker in the jungle? Too many cheetahs. What sounds like a sneeze and is made of leather? A shoe. How do you stop a bull from charging? You cancel its credit card. Why was the math book sad? It had too many problems. Why are fish so smart? Because they swim in schools. Why did the employee get fired from the keyboard factory? He wasn’t putting in enough shifts. Did you hear about the man who cut off his left leg? He’s all right now. Did you hear the one about the claustrophobic astronaut? He just needed a little space. What kind of music should you listen to while fishing? Something catchy! What do you call a girl in the middle of a tennis court? Annette. What did the ocean say to the beach? Nothing. It just waved. What did one wall say to the other? I’ll meet you at the corner. Why did the nose feel sad? It was always getting picked on. Did you hear about the cold dinner? It was chili. Why did the deer go to the dentist? It had buck teeth. Why can’t you trust a balloon? It’s full of hot air A cheese factory exploded in France. Da brie is everywhere! Not sure if you have noticed, but I love bad puns. That’s just how eye roll. Why did the banana go to the doctor? Because it wasn’t peeling well. Where does a sheep go to get a haircut? The baa baa shop. What did the mama  say to the baby ? It’s pasture bed time. Why should you never use a dull pencil? Because it’s pointless. Why did the cookie go to the doctor? It was feeling crumby. Where did the cat go after losing its tail? The retail store. Why don’t eggs tell jokes? They’d crack each other up. What kind of sandals do frogs wear? Open-toad. What do you call a herd of sheep falling down a hill? A lambslide. How do you organize a space party? You planet. How many tickles does it take to make an octopus laugh? Ten tickles. What do you call a potato wearing glasses? A spec-tater. What do you call a moose with no name? Anonymoose. Why did the ram run over the cliff? He didn’t see the ewe turn. Why did the picture go to jail? He was framed. What is a calendar’s favorite food? Dates. Why was the football stadium cold? There were too many fans. Why do bananas wear sunscreen? Because they peel. Why do bees have sticky hair? Because they use honey combs. Why did the watch go on vacation? To unwind. How does a penguin build a house? Igloos it together. Why do melons have weddings? Because they cantaloupe. Why did the computer get glasses? To improve its website. What did the blanket say to the bed? I’ve got you covered. What did the roof say to the shingle? The first one’s on the house. What do you call birds that stick together? Velcrows Why did the duck fall on the sidewalk? He tripped on a quack. How do birds learn to fly? They wing it. Did you hear about the walnut and cashew that threw a party? It was nuts. Did the hear about the ice cream truck accident? It crashed on a rocky road. What kind of bird works on a construction site? A crane. What did one elevator say to the other elevator? I think I’m coming down with something. What did the hamburger name its baby? Patty. What type of music do the planets enjoy? Neptunes. Why did the phone wear glasses? Because it lost all its contacts. Why do bakers work so hard? Because they knead dough. Why are fish so easy to weigh? Because they have their own set of scales. What do you call a priest that becomes a lawyer? A father-in-law. What do you give a scientist with bad breath? Experi-mints. What did Benjamin Franklin say when he discovered electricity? Nothing. He was too shocked. What do you call a medieval lamp? A knight light. What did one hat say to the other? You go on ahead. Why did the frog take the bus to work? His car got toad. What does an evil hen lay? Deviled eggs. How can you tell the difference between a dog and tree? By their bark. Why do dragons sleep during the day? Because they like to fight knights. Why did the scarecrow win an award? It was outstanding in its field. Did you hear about the 12-inch dog? It was a foot long. Why did the baseball player get arrested? He stole third base. What did one piece of tape say to the other? Let’s stick together. What's brown and sticky? A stick. How does the rancher keep track of his cattle? With a -culator. What do you call a shoe made out of a banana? A slipper. How you fix a broken pumpkin? With a pumpkin patch. Where do boats go when they’re sick? To the dock. Can February March? No, but April May! What do you call a fibbing cat? A lion. Did you hear the rumor about butter? Well, I’m not going to go spreading it! Where do you learn to make ice cream? Sundae school. What’s a scarecrow’s favorite fruit? Straw-berries Where do burgers go dancing? At the meatball. What time do ducks wake up? At the quack of dawn. Why was the broom late? It over-swept. What kind of tree fits in your hand? A palm tree. Where do books hide when they’re afraid? Under their covers. How do trees get on the internet? They log in. What does a painter do when he gets cold? Puts on another coat. What did the calculator say to the pencil? You can count on me. What has four wheels and flies? A garbage truck. What do you call two ducks and a ? Quackers and milk. What do s like to read? Cattle-logs. How did the farmer fix his torn overalls? With a cabbage patch. How much money does a skunk have? Just one scent. What do you get when you cross an elephant and a fish? Swimming trunks. What kind of cereal do leprechauns eat? Lucky Charms. What do you call recently-married spiders? Newly-webs. Where do crayons go on vacation? Color-ado. What do you get when you cross a Smurf and a ? Blue cheese. What happens when ice cream gets angry? It has a meltdown. What do you call a locomotive carrying bubble gum? A chew chew train. How do you get a mouse to smile? Say “cheese.” Why couldn’t the bike stand up on its own? It was too tired. What do you call a sheep that knows karate? A lamb chop. Why did the snowman buy a bag of carrots? He wanted to pick his nose. What did the Dalmatian say after dinner? That hit the spot. How do you know when a bike is thinking? You can see its wheels turning. What does a librarian use to go fishing? A bookworm. What did one leaf say to the other? I’m falling for you. Where’s the one place you should never take your dog? A flea market. How does Darth Vader like his bagels? On the dark side. What do you call spaghetti in disguise? An impasta. Why did the tailor get fired? He wasn’t a good fit. Where do elephants store luggage? In a trunk. Why did the poodle buy a clock? It wanted to be a watch dog. Why do birds fly south? Because it’s too far to talk. What do you call a fly with a sore throat? A hoarse fly. Dogs can’t operate MRI machines — but cats-can. If you see a robbery at an Apple store, does that make you an iWitness? I had a date last night. It was perfect. Tomorrow, I’ll have a grape. Justice is a dish best served cold. If it were served warm, it would be just-water. It was an emotional wedding — even the cake was in tiers. Why did Waldo go to therapy? To find himself. I have an inferiority complex, but it’s not a very good one. Our vacuum cleaner is getting old. It's just gathering dust. Why did the thief take a shower before robbing the bank? He wanted to make a clean getaway. What do lawyers wear to work? Law suits. Why was the traffic light late to work? It took too long to change. Why do hamburgers go south for the winter? So they don’t freeze their buns. Why didn’t the sun go to college? It already had a million degrees. What do you call someone who can’t stick to a diet? A desserter. Why did the little strawberry cry? His mom was in a jam. Why couldn’t the toilet paper cross the road? It got stuck in a crack. What do you get from a pampered ? Spoiled milk. Why did the whale blush? It saw the ocean’s bottom. Getting paid to sleep would be my dream job. I used to be a banker, but I lost interest. Why can’t you trust an atom? Because they make up everything. I went to buy a pair of camouflage pants, but I couldn’t find any. Why did the tomato blush? It saw the salad dressing. I haven’t talked to my wife in a week — I didn’t want to interrupt her. Why are pigs bad drivers? They hog the road. I’m so good at sleeping, I can do it with my eyes closed! Why did police arrest the turkey? They suspected fowl play. What do computers eat for a snack? Microchips. How do frogs invest their money? They use a stock croaker. Did you hear about the whale that swallowed a clown? It felt funny after. The past, present and future walked into a bar. It was tense. "
    ):
        print("Kamikaze kitty")
    else:
        print("Your cowless variable is incorrect.")


def test3_8(answer):
    if answer == 11.0:
        print("Cowabunga")
    else:
        print("Your cow_joke_count variable is incorrect.")


def test3_9(answer):
    if answer == 0.06111111111111111:
        print("Cowifornia")
    else:
        print("Your cow_joke_perc variable is incorrect.")


# Project 3 Problem 5
def test3_10(answer):
    if answer == {"fish": 4, "cow": 7, "cheese": 3, "dog": 6, "birds": 3, "tree": 3}:
        print("Kangarodeo")
    else:
        print("Your word_dict dictionary is incorrect.")


# Project 3 Problem 6
def test3_11(answer):
    if answer == [
        ("fish", 4),
        ("cow", 7),
        ("cheese", 3),
        ("dog", 6),
        ("birds", 3),
        ("tree", 3),
    ]:
        print("Strazbanana")
    else:
        print("Your word_tuples list is incorrect.")


# Project 4
def severity_score_test(c):
    if c == "None":
        return 0
    elif c == "Mild":
        return 1
    elif c == "Moderate":
        return 2
    else:
        return 3


# Project 4 Problem 1
def movie_info_test(url):
    headers = requests.utils.default_headers()
    headers.update(
        {
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0",
        }
    )
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    title = soup.find("title").text
    title2 = re.search(r"([^0-9(]+)", title).group(1).strip()
    rating = soup.findAll(
        "div", attrs={"data-testid": "hero-rating-bar__aggregate-rating__score"}
    )[0].text
    rating2 = re.search(r"(.*)\/10", rating).group(1).strip()
    content_rating = soup.findAll(
        "a", class_="ipc-link ipc-link--baseAlt ipc-link--inherit-color"
    )[-1].text

    # Get the parental guide stuff
    new_url = url + "parentalguide"
    response = requests.get(new_url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    nudity_section = soup.find_all("section", attrs={"id": "advisory-nudity"})
    sex_nudity = nudity_section[0].find_all("span")[0].text
    violence_section = soup.find_all("section", attrs={"id": "advisory-violence"})
    violence = violence_section[0].find_all("span")[0].text
    profanity_section = soup.find_all("section", attrs={"id": "advisory-profanity"})
    profanity = profanity_section[0].find_all("span")[0].text
    drugs_section = soup.find_all("section", attrs={"id": "advisory-alcohol"})
    drugs = drugs_section[0].find_all("span")[0].text
    frightening_section = soup.find_all("section", attrs={"id": "advisory-frightening"})
    frightening = frightening_section[0].find_all("span")[0].text
    sex_nudity_score = severity_score_test(sex_nudity)
    violence_score = severity_score_test(violence)
    profanity_score = severity_score_test(profanity)
    drugs_score = severity_score_test(drugs)
    frightening_score = severity_score_test(frightening)

    # create dictionary
    film_info = {
        "movie_title": title2,
        "rating": float(rating2),
        "content_rating": content_rating,
        "sex_nudity": sex_nudity_score,
        "violence": violence_score,
        "profanity": profanity_score,
        "drugs": drugs_score,
        "frightening": frightening_score,
    }

    return film_info


def test4_1(url, answer):
    test = movie_info_test(url)
    incorrect_answers = []

    if test["movie_title"] != answer["movie_title"]:
        incorrect_answers.append("Your movie_title value is incorrect for this film")

    if test["rating"] != answer["rating"]:
        incorrect_answers.append("Your rating value is incorrect  for this film")

    if test["content_rating"] != answer["content_rating"]:
        incorrect_answers.append("Your content_rating value is incorrect for this film")

    if test["sex_nudity"] != answer["sex_nudity"]:
        incorrect_answers.append("Your sex_nudity value is incorrect for this film")

    if test["violence"] != answer["violence"]:
        incorrect_answers.append("Your violence value is incorrect for this film")

    if test["profanity"] != answer["profanity"]:
        incorrect_answers.append("Your profanity value is incorrect for this film")

    if test["drugs"] != answer["drugs"]:
        incorrect_answers.append("Your drugs value is incorrect for this film")

    if test["frightening"] != answer["frightening"]:
        incorrect_answers.append("Your frightening value is incorrect for this film")

    if not incorrect_answers:
        print("Wilderpeople")
    else:
        print([x for x in incorrect_answers])


def test4_2(url, answer):
    test = movie_info_test(url)
    incorrect_answers = []

    if test["movie_title"] != answer["movie_title"]:
        incorrect_answers.append("Your movie_title value is incorrect for this film")

    if test["rating"] != answer["rating"]:
        incorrect_answers.append("Your rating value is incorrect  for this film")

    if test["content_rating"] != answer["content_rating"]:
        incorrect_answers.append("Your content_rating value is incorrect for this film")

    if test["sex_nudity"] != answer["sex_nudity"]:
        incorrect_answers.append("Your sex_nudity value is incorrect for this film")

    if test["violence"] != answer["violence"]:
        incorrect_answers.append("Your violence value is incorrect for this film")

    if test["profanity"] != answer["profanity"]:
        incorrect_answers.append("Your profanity value is incorrect for this film")

    if test["drugs"] != answer["drugs"]:
        incorrect_answers.append("Your drugs value is incorrect for this film")

    if test["frightening"] != answer["frightening"]:
        incorrect_answers.append("Your frightening value is incorrect for this film")

    if not incorrect_answers:
        print("Gravity Falls")
    else:
        print([x for x in incorrect_answers])


def test4_3(url, answer):
    test = movie_info_test(url)
    incorrect_answers = []

    if test["movie_title"] != answer["movie_title"]:
        incorrect_answers.append("Your movie_title value is incorrect for this film")

    if test["rating"] != answer["rating"]:
        incorrect_answers.append("Your rating value is incorrect  for this film")

    if test["content_rating"] != answer["content_rating"]:
        incorrect_answers.append("Your content_rating value is incorrect for this film")

    if test["sex_nudity"] != answer["sex_nudity"]:
        incorrect_answers.append("Your sex_nudity value is incorrect for this film")

    if test["violence"] != answer["violence"]:
        incorrect_answers.append("Your violence value is incorrect for this film")

    if test["profanity"] != answer["profanity"]:
        incorrect_answers.append("Your profanity value is incorrect for this film")

    if test["drugs"] != answer["drugs"]:
        incorrect_answers.append("Your drugs value is incorrect for this film")

    if test["frightening"] != answer["frightening"]:
        incorrect_answers.append("Your frightening value is incorrect for this film")

    if not incorrect_answers:
        print("Gruncle Stan")
    else:
        print([x for x in incorrect_answers])


# Project 5
def content_scoring_test(r):
    if r == "G":
        return 0
    elif r == "PG":
        return 1
    elif r == "PG-13":
        return 2
    elif r == "R":
        return 3
    else:
        return 4


def movie_filter_test(movie_tuples):
    movies_list = []
    omdb.set_default("apikey", "c0e2b3c2")
    for m in movie_tuples:
        movie = omdb.get(title=m[0], year=m[1], fullplot=True)
        if movie == {}:
            continue
        content = movie["rated"]
        content_score = content_scoring_test(content)
        genres = movie["genre"]
        try:
            imdb_rating = float(movie["imdb_rating"])
        except:
            imdb_rating = 0
        try:
            rotten_rating = int(movie["ratings"][1]["value"][:-1])
        except:
            rotten_rating = 0
        try:
            meta_rating = int(movie["ratings"][2]["value"][:-4])
        except:
            meta_rating = 0
        movie_list = [
            m[0],
            m[1],
            content,
            genres,
            imdb_rating,
            rotten_rating,
            meta_rating,
        ]
        movies_list.append(movie_list)

    return movies_list


def filter_test(
    movies_list, content=None, genre=None, imdb=None, rotten=None, meta=None
):
    keeper_movies = []
    for m in movies_list:
        if content:
            if content_scoring_test(m[2]) <= content_scoring_test(content):
                pass
            else:
                continue
        if genre:
            if genre in m[3]:
                pass
            else:
                continue
        if imdb:
            if m[4] >= imdb:
                pass
            else:
                continue
        if rotten:
            if m[5] >= rotten:
                pass
            else:
                continue
        if meta:
            if m[6] >= meta:
                pass
            else:
                continue
        keeper_movies.append(m)
    return keeper_movies


# Project 5 Problem 1
def test5_1(
    answer, movies, content=None, genre=None, imdb=None, rotten=None, meta=None
):
    movie_list = movie_filter_test(movies)
    filtered_movies = filter_test(movie_list, content=content, genre=genre)

    if filtered_movies == answer:
        print("Angry Angels")
    else:
        print(
            "Your function failed for the parameters 'movie_filter(all_movies, 'G', genre='Animation')'"
        )


def test5_2(
    answer, movies, content=None, genre=None, imdb=None, rotten=None, meta=None
):
    movie_list = movie_filter_test(movies)
    filtered_movies = filter_test(movie_list, content=content, imdb=imdb)

    if filtered_movies == answer:
        print("Haunted Hot Dogs")
    else:
        print(
            "Your function failed for the parameters 'movie_filter(all_movies, 'R', imdb=8.0)'"
        )


def test5_3(
    answer, movies, content=None, genre=None, imdb=None, rotten=None, meta=None
):
    movie_list = movie_filter_test(movies)
    filtered_movies = filter_test(movie_list, content=content, rotten=rotten)

    if filtered_movies == answer:
        print("Goat Warriors")
    else:
        print(
            "Your function failed for the parameters 'movie_filter(all_movies, 'PG', rotten_filter=60)'"
        )


def test5_4(
    answer, movies, content=None, genre=None, imdb=None, rotten=None, meta=None
):
    movie_list = movie_filter_test(movies)
    filtered_movies = filter_test(movie_list, content=content, meta=meta)

    if filtered_movies == answer:
        print("Fully Automatic PEZ Dispensers")
    else:
        print(
            "Your function failed for the parameters 'movie_filter(all_movies, 'PG-13', meta_filter=75)'"
        )


# Project 6 Problem 1
def test6_1(answer):
    test = [
        (
            "tconst",
            "titleType",
            "primaryTitle",
            "originalTitle",
            "isAdult",
            "startYear",
            "endYear",
            "runtimeMinutes",
            "genres",
        ),
        (
            "tt0000001",
            "short",
            "Carmencita",
            "Carmencita",
            0,
            1894,
            "\\N",
            1,
            "Documentary,Short",
        ),
        (
            "tt0000002",
            "short",
            "Le clown et ses chiens",
            "Le clown et ses chiens",
            0,
            1892,
            "\\N",
            5,
            "Animation,Short",
        ),
        (
            "tt0000003",
            "short",
            "Pauvre Pierrot",
            "Pauvre Pierrot",
            0,
            1892,
            "\\N",
            4,
            "Animation,Comedy,Romance",
        ),
        (
            "tt0000004",
            "short",
            "Un bon bock",
            "Un bon bock",
            0,
            1892,
            "\\N",
            12,
            "Animation,Short",
        ),
        (
            "tt0000005",
            "short",
            "Blacksmith Scene",
            "Blacksmith Scene",
            0,
            1893,
            "\\N",
            1,
            "Comedy,Short",
        ),
        (
            "tt0000006",
            "short",
            "Chinese Opium Den",
            "Chinese Opium Den",
            0,
            1894,
            "\\N",
            1,
            "Short",
        ),
        (
            "tt0000007",
            "short",
            "Corbett and Courtney Before the Kinetograph",
            "Corbett and Courtney Before the Kinetograph",
            0,
            1894,
            "\\N",
            1,
            "Short,Sport",
        ),
        (
            "tt0000008",
            "short",
            "Edison Kinetoscopic Record of a Sneeze",
            "Edison Kinetoscopic Record of a Sneeze",
            0,
            1894,
            "\\N",
            1,
            "Documentary,Short",
        ),
        (
            "tt0000009",
            "movie",
            "Miss Jerry",
            "Miss Jerry",
            0,
            1894,
            "\\N",
            45,
            "Romance",
        ),
    ]
    if answer == test:
        print("Bippity Boppity Boo")
    else:
        print(
            "Your result for 'SELECT * FROM movies_basics ORDER BY tconst LIMIT 10' does not match the expected result."
        )


def test6_2(answer):
    test = [
        (
            "tt0102291",
            "movie",
            "Der letzte Winter",
            "Der letzte Winter",
            0,
            1991,
            "\\N",
            55,
            "Drama",
        ),
        (
            "tt0102290",
            "tvMovie",
            "Not Mozart: Letters, Riddles and Writs",
            "Not Mozart: Letters, Riddles and Writs",
            0,
            1991,
            "\\N",
            30,
            "\\N",
        ),
        (
            "tt0102289",
            "tvMovie",
            "Lethal Innocence",
            "Lethal Innocence",
            0,
            1991,
            "\\N",
            90,
            "Drama",
        ),
        (
            "tt0102288",
            "movie",
            "Let Him Have It",
            "Let Him Have It",
            0,
            1991,
            "\\N",
            115,
            "Crime,Drama,History",
        ),
        ("tt0102287", "tvMovie", "Leporella", "Leporella", 0, 1991, "\\N", 74, "Drama"),
        (
            "tt0102286",
            "movie",
            "Tiger Cage III",
            "Leng mian ju ji shou",
            0,
            1991,
            "\\N",
            94,
            "Action",
        ),
        (
            "tt0102285",
            "movie",
            "Lena's Holiday",
            "Lena's Holiday",
            0,
            1991,
            "\\N",
            100,
            "Comedy,Romance,Thriller",
        ),
        (
            "tt0102284",
            "movie",
            "Leise Schatten",
            "Leise Schatten",
            0,
            1992,
            "\\N",
            91,
            "Drama",
        ),
        (
            "tt0102283",
            "movie",
            "Legal Tender",
            "Legal Tender",
            0,
            1991,
            "\\N",
            95,
            "Action,Thriller",
        ),
        (
            "tt0102282",
            "movie",
            "Lebewohl, Fremde",
            "Lebewohl, Fremde",
            0,
            1991,
            "\\N",
            100,
            "Drama,Romance",
        ),
    ]
    if answer == test:
        print("Alakazam!")
    else:
        print(
            "Your result for 'SELECT * FROM movies_basics ORDER BY tconst DESC LIMIT 10' does not match the expected result."
        )


# Project 7 Problem 1
def test7_1(answer):
    test = [
        ("tconst", "directors", "writers"),
        ("tt0000001", "nm0005690", "\\N"),
        ("tt0000002", "nm0721526", "\\N"),
        ("tt0000003", "nm0721526", "\\N"),
        ("tt0000004", "nm0721526", "\\N"),
        ("tt0000005", "nm0005690", "\\N"),
        ("tt0000006", "nm0005690", "\\N"),
        ("tt0000007", "nm0005690,nm0374658", "\\N"),
        ("tt0000008", "nm0005690", "\\N"),
        ("tt0000009", "nm0085156", "nm0085156"),
    ]
    if answer == test:
        print("Succotash")
    else:
        print(
            "Your result for 'SELECT * FROM movies_crew ORDER BY tconst LIMIT 10' does not match the expected result."
        )


def test7_2(answer):
    test = [
        ("tt0102291", "nm0881355", "\\N"),
        ("tt0102290", "nm0310561,nm0628430", "nm0310561,nm0628430,nm0006219"),
        ("tt0102289", "nm0926301", "nm0926301"),
        ("tt0102288", "nm0575389", "nm0701031,nm0905498"),
        ("tt0102287", "nm0198699", "nm0198699,nm0959003"),
        ("tt0102286", "nm0950759", "nm2060068,nm0504980"),
        ("tt0102285", "nm0450661", "nm0863503,nm0450661"),
        ("tt0102284", "nm0394776", "nm0394776"),
        ("tt0102283", "nm0612730", "nm0730848"),
        ("tt0102282", "nm0059725", "nm0059725"),
    ]
    if answer == test:
        print("Sassafras")
    else:
        print(
            "Your result for 'SELECT * FROM movies_crew ORDER BY tconst DESC LIMIT 10' does not match the expected result."
        )


# Project 7 Problem 2
def test7_3(answer):
    test = [
        ("tconst", "averageRating", "numVotes"),
        ("tt0000001", 5.7, 1993),
        ("tt0000002", 5.8, 268),
        ("tt0000003", 6.5, 1879),
        ("tt0000004", 5.5, 177),
        ("tt0000005", 6.2, 2662),
        ("tt0000006", 5.0, 182),
        ("tt0000007", 5.4, 834),
        ("tt0000008", 5.4, 2136),
        ("tt0000009", 5.3, 206),
    ]
    if answer == test:
        print("Marmalade")
    else:
        print(
            "Your result for 'SELECT * FROM movies_ratings ORDER BY tconst LIMIT 10' does not match the expected result."
        )


def test7_4(answer):
    test = [
        ("tt0139287", 6.8, 12),
        ("tt0139286", 6.1, 13),
        ("tt0139283", 6.8, 102),
        ("tt0139276", 7.1, 105),
        ("tt0139275", 5.7, 136),
        ("tt0139274", 5.2, 140),
        ("tt0139272", 5.5, 140),
        ("tt0139269", 5.7, 26),
        ("tt0139267", 5.1, 22),
        ("tt0139266", 5.3, 113),
    ]
    if answer == test:
        print("Periwinkle")
    else:
        print(
            "Your result for 'SELECT * FROM movies_ratings ORDER BY tconst DESC LIMIT 10' does not match the expected result."
        )


# Project 7 Problem 3
def test7_5(answer):
    test = [
        ("The Simpsons", 8.7, 424381),
        ("Star Wars: Episode IV - A New Hope", 8.6, 1414060),
        ("Mr. Bean", 8.6, 128266),
        ("Apocalypse Now", 8.4, 692100),
        ("Amadeus", 8.4, 416996),
        ("Network", 8.1, 165776),
        ("Dog Day Afternoon", 8.0, 267726),
        ("The Conversation", 7.8, 117551),
        ("Serpico", 7.7, 130667),
        ("The Godfather Part III", 7.6, 413886),
    ]
    if answer == test:
        print("Vantablack")
    else:
        print(
            "Your query does not return the expected results. The top 10 expected films (not in order) are: The Godfather Part III, The Conversation, Network, Apocalypse Now, Star Wars: Episode IV - A New Hope, Sercipo, Dog Day Afternoon, Amadeus, Mr. Bean, The Simpsons"
        )


# Project 9
# Question 1
def test9_1(answer):
    if answer == "cool_stuff":
        print("Taco Tornado")
    else:
        print("Your answer is incorrect.")


# Question 2
def test9_2(answer):
    if answer == "cool_stuff":
        print("Enchilada Earthquake")
    else:
        print("Your answer is incorrect.")


# Question 3
def test9_3(answer):
    if answer == "1f50f920176fa81dab994f9023523100":
        print("Hummus Hurricane")
    else:
        print("Your answer is incorrect.")


# Question 4
def test9_4(answer):
    if answer == "consoles_games":
        print("Hamburger Hailstorm")
    else:
        print("Your answer is incorrect.")


# Question 5
def test9_5(answer):
    data = {
        "month": [
            "2017-01",
            "2017-02",
            "2017-03",
            "2017-04",
            "2017-05",
            "2017-06",
            "2017-07",
            "2017-08",
            "2017-09",
            "2017-10",
            "2017-11",
            "2017-12",
        ],
        "avg_order": [
            169.92,
            161.36,
            159.92,
            170.99,
            158.16,
            154.14,
            146.01,
            156.35,
            179.7,
            168.13,
            159.41,
            150.89,
        ],
    }
    df = pd.DataFrame(data)
    if answer == df:
        print("French Fries Flash Flood")
    else:
        print("Your answer is incorrect.")


# Question 6
def test9_6(answer1, answer2):
    if answer1 == 4.29 and answer2 == 2.35:
        print("Avocado Avalanche")
    else:
        print("Your answer is incorrect.")


# Question 7
def test9_7(answer):
    if answer == 0.51:
        print("Lasagna Lighting Storm")
    else:
        print("Your answer is incorrect.")
