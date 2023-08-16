"""
 Copyright (c) 2023, salesforce.com, inc.
 All rights reserved.
 SPDX-License-Identifier: Apache License 2.0
 For full license text, see the LICENSE file in the repo root or https://www.apache.org/licenses/LICENSE-2.0
"""
zeroshot = """Following the instruction to simulate the web shopping. Based on your observation, you may operate one of the following actions
search: using this action to search products.
click: click observed [button], the clickable buttons are in [], for example click [Back to Search] can return back to research.
Use your best knowledge and take actions. You response should follow action[detail] format, such as search[3 ounce bright citrus deodorant sensitive skin], click[B078GWRC1J], click[bright citrus].
"""

zeroshot_think = """You are simulating web shopping. Based on your observation, you may operate one of the following actions:
search: using this action to search products.
think: using this action to plan your actions and reasoning.
click: using this action to click observed [button], the clickable buttons are in [], for example click [Back to Search] can return back to research.
Use your best knowledge and take actions. You response should follow action[detail] format, such as search[3 ounce bright citrus deodorant sensitive skin], think[B078GWRC1J and B078GTKVXY are bright citrus deodorant less then 50 dollars. I can check B078GWRC1J first.], click[B078GWRC1J], click[bright citrus].
"""

oneshot = """Webshop 
Instruction:  
i would like a 3 ounce bottle of bright citrus deodorant for sensitive skin, and price lower than 50.00 dollars 
[Search]  

Action: search[3 ounce bright citrus deodorant sensitive skin]
Observation: 
[Back to Search] 
Page 1 (Total results: 50) 
[Next >] 
[B078GWRC1J] 
Bright Citrus Deodorant by Earth Mama | Natural and Safe for Sensitive Skin, Pregnancy and Breastfeeding, Contains Organic Calendula 3-Ounce 
$10.99 
[B078GTKVXY] 
Ginger Fresh Deodorant by Earth Mama | Natural and Safe for Sensitive Skin, Pregnancy and Breastfeeding, Contains Organic Calendula 3-Ounce 
$10.99 
[B08KBVJ4XN] 
Barrel and Oak - Aluminum-Free Deodorant, Deodorant for Men, Essential Oil-Based Scent, 24-Hour Odor Protection, Cedar & Patchouli Blend, Gentle on Sensitive Skin (Mountain Sage, 2.7 oz, 2-Pack) 
$15.95  

Action: think[B078GWRC1J and B078GTKVXY are bright citrus deodorant less then 50 dollars. I can check B078GWRC1J first.]
Observation: OK.

Action: click[B078GWRC1J]
Observation: 
[Back to Search] 
[< Prev] 
scent [assorted scents][bright citrus][calming lavender][ginger fresh][simply non-scents]
size [travel set (4-pack)][3 ounce (pack of 1)][3-ounce (2-pack)]
Bright Citrus Deodorant by Earth Mama | Natural and Safe for Sensitive Skin, Pregnancy and Breastfeeding, Contains Organic Calendula 3-Ounce 
Price: $10.99 
Rating: N.A. 
[Description] 
[Features] 
[Reviews] 
[Buy Now]  

Action: think[For 3 ounce bottle of bright citrus deodorant for sensitive skin, the item has options 'bright citrus' and '3 ounce (pack of 1)' and seems good to buy.]
Observation: OK.

Action: click[bright citrus]
Observation: You have clicked bright citrus. 

Action: click[3 ounce (pack of 1)]
Observation: You have clicked 3 ounce (pack of 1). 

Action: click[Buy Now]
"""

plan = """Webshop 
Instruction: i would like a 3 ounce bottle of bright citrus deodorant for sensitive skin, and price lower than 50.00 dollars. 
Plan: First, I need to search[3 ounce bright citrus deodorant sensitive skin]. Next, I need to click the most relevant item to get more details, e.g. click[B078GWRC1J]. Next, if this item is not what I want, I will click[< Prev] to check other searching results or I can click[Back to Search] to search with different keywords. If I find one item meets the instruction requirements, I will click necessary options, such as click[bright citrus] and click[3 ounce (pack of 1)]. Finally, I will click[Buy Now] to complete the shopping.
"""

oneshot_plan = """Webshop 
Instruction: i would like a 3 ounce bottle of bright citrus deodorant for sensitive skin, and price lower than 50.00 dollars. 
Plan: First, I need to search[3 ounce bright citrus deodorant sensitive skin]. Next, I need to click the most relevant item to get more details, e.g. click[B078GWRC1J]. Next, if this item is not what I want, I will click[< Prev] to check other searching results or I can click[Back to Search] to search with different keywords. If I find one item meets the instruction requirements, I will click necessary options, such as click[bright citrus] and click[3 ounce (pack of 1)]. Finally, I will click[Buy Now] to complete the shopping.

Action: search[3 ounce bright citrus deodorant sensitive skin]
Observation: 
[Back to Search] 
Page 1 (Total results: 50) 
[Next >] 
[B078GWRC1J] 
Bright Citrus Deodorant by Earth Mama | Natural and Safe for Sensitive Skin, Pregnancy and Breastfeeding, Contains Organic Calendula 3-Ounce 
$10.99 
[B078GTKVXY] 
Ginger Fresh Deodorant by Earth Mama | Natural and Safe for Sensitive Skin, Pregnancy and Breastfeeding, Contains Organic Calendula 3-Ounce 
$10.99 
[B08KBVJ4XN] 
Barrel and Oak - Aluminum-Free Deodorant, Deodorant for Men, Essential Oil-Based Scent, 24-Hour Odor Protection, Cedar & Patchouli Blend, Gentle on Sensitive Skin (Mountain Sage, 2.7 oz, 2-Pack) 
$15.95 

Action: click[B078GWRC1J]
Observation:
[Back to Search]
[< Prev]
scent [assorted scents][bright citrus][calming lavender][ginger fresh][simply non-scents]
size [travel set (4-pack)][3 ounce (pack of 1)][3-ounce (2-pack)]
Bright Citrus Deodorant by Earth Mama | Natural and Safe for Sensitive Skin, Pregnancy and Breastfeeding, Contains Organic Calendula 3-Ounce 
Price: $10.99
Rating: N.A.
[Description]
[Features]
[Reviews]
[Buy Now]

Action: click[bright citrus]
Observation: You have clicked bright citrus.

Action: click[3 ounce (pack of 1)]
Observation: You have clicked 3 ounce (pack of 1). 

Action: click[Buy Now]
"""

plan_react = """Webshop 
Instruction: i would like a 3 ounce bottle of bright citrus deodorant for sensitive skin, and price lower than 50.00 dollars. 
Plan: First, I need to search[3 ounce bright citrus deodorant sensitive skin]. Next, I need to think[some items are bright citrus deodorant less then 50 dollars. I can check one first.]. Next, I need to click the most relevant item to get more details, e.g. click[B078GWRC1J]. If I need think whether this item meets the requirements, e.g. think[For 3 ounce bottle of bright citrus deodorant for sensitive skin, the item has options 'bright citrus' and '3 ounce (pack of 1)' and seems good to buy.]. Then, I will click necessary options, such as click[bright citrus] and click[3 ounce (pack of 1)]. Finally, I will click[Buy Now] to complete the shopping.
"""

oneshot_plan_react = """Webshop 
Instruction:  
i would like a 3 ounce bottle of bright citrus deodorant for sensitive skin, and price lower than 50.00 dollars 
[Search]  

Action: search[3 ounce bright citrus deodorant sensitive skin]
Observation: 
[Back to Search] 
Page 1 (Total results: 50) 
[Next >] 
[B078GWRC1J] 
Bright Citrus Deodorant by Earth Mama | Natural and Safe for Sensitive Skin, Pregnancy and Breastfeeding, Contains Organic Calendula 3-Ounce 
$10.99 
[B078GTKVXY] 
Ginger Fresh Deodorant by Earth Mama | Natural and Safe for Sensitive Skin, Pregnancy and Breastfeeding, Contains Organic Calendula 3-Ounce 
$10.99 
[B08KBVJ4XN] 
Barrel and Oak - Aluminum-Free Deodorant, Deodorant for Men, Essential Oil-Based Scent, 24-Hour Odor Protection, Cedar & Patchouli Blend, Gentle on Sensitive Skin (Mountain Sage, 2.7 oz, 2-Pack) 
$15.95  

Action: think[B078GWRC1J and B078GTKVXY are bright citrus deodorant less then 50 dollars. I can check B078GWRC1J first.]
Observation: OK.

Action: click[B078GWRC1J]
Observation: 
[Back to Search] 
[< Prev] 
scent [assorted scents][bright citrus][calming lavender][ginger fresh][simply non-scents]
size [travel set (4-pack)][3 ounce (pack of 1)][3-ounce (2-pack)]
Bright Citrus Deodorant by Earth Mama | Natural and Safe for Sensitive Skin, Pregnancy and Breastfeeding, Contains Organic Calendula 3-Ounce 
Price: $10.99 
Rating: N.A. 
[Description] 
[Features] 
[Reviews] 
[Buy Now]  

Action: think[For 3 ounce bottle of bright citrus deodorant for sensitive skin, the item has options 'bright citrus' and '3 ounce (pack of 1)' and seems good to buy.]
Observation: OK.

Action: click[bright citrus]
Observation: You have clicked bright citrus. 

Action: click[3 ounce (pack of 1)]
Observation: You have clicked 3 ounce (pack of 1). 

Action: click[Buy Now]
"""

search = """Webshop 
Instruction:
i'm looking for a yellow hair styling product that is made from natural ingredients and easy to use, and price lower than 40.00 dollars
You have already search[yellow hair styling product made from natural ingredients easy to use price < 40.00 dollars]. Could you please change your search query?

Action: search[yellow hair styling natural ingredients]

Instruction:  
i would like a 3 ounce bottle of bright citrus deodorant for sensitive skin, and price lower than 50.00 dollars 

Action: search[3 ounce bright citrus deodorant sensitive skin]

Instruction:
i am looking for black pull-out organizers with nickel finish and size must be 15\" wide, and price lower than 90.00 dollars

Action: search[black pull-out organizers with nickel finish, 15\" wide]
"""

click = """Webshop 
Instruction:  
i would like a 3 ounce bottle of bright citrus deodorant for sensitive skin, and price lower than 50.00 dollars 
[Search]  

search[3 ounce bright citrus deodorant sensitive skin]
Observation: 
[Back to Search] 
Page 1 (Total results: 50) 
[Next >] 
[B078GWRC1J] 
Bright Citrus Deodorant by Earth Mama | Natural and Safe for Sensitive Skin, Pregnancy and Breastfeeding, Contains Organic Calendula 3-Ounce 
$10.99 
[B078GTKVXY] 
Ginger Fresh Deodorant by Earth Mama | Natural and Safe for Sensitive Skin, Pregnancy and Breastfeeding, Contains Organic Calendula 3-Ounce 
$10.99 
[B08KBVJ4XN] 
Barrel and Oak - Aluminum-Free Deodorant, Deodorant for Men, Essential Oil-Based Scent, 24-Hour Odor Protection, Cedar & Patchouli Blend, Gentle on Sensitive Skin (Mountain Sage, 2.7 oz, 2-Pack) 
$15.95
current available action is click:[Back to Search\tB078GWRC1J\tB078GTKVXY\tB08KBVJ4XN]

Action: click[B078GWRC1J]
Observation: 
[Back to Search] 
[< Prev] 
scent [assorted scents][bright citrus][calming lavender][ginger fresh][simply non-scents]
size [travel set (4-pack)][3 ounce (pack of 1)][3-ounce (2-pack)]
Bright Citrus Deodorant by Earth Mama | Natural and Safe for Sensitive Skin, Pregnancy and Breastfeeding, Contains Organic Calendula 3-Ounce 
Price: $10.99 
Rating: N.A. 
[Description] 
[Features] 
[Reviews]
[Buy Now]
current available action is click:[Back to Search\t< Prev\tassorted scents\tbright citrus\tcalming lavender\tginger fresh\tsimply non-scents\ttravel set (4-pack)\t3 ounce (pack of 1)\t3-ounce (2-pack)\tDescription\tFeatures\tReviews\tBuy Now]

Action: click[bright citrus]
Observation: You have clicked bright citrus.
current available action is click:[Back to Search\t< Prev\tassorted scents\tbright citrus\tcalming lavender\tginger fresh\tsimply non-scents\ttravel set (4-pack)\t3 ounce (pack of 1)\t3-ounce (2-pack)\tDescription\tFeatures\tReviews\tBuy Now]

Action: click[3 ounce (pack of 1)]
Observation: You have clicked 3 ounce (pack of 1). 
current available action is click:[Back to Search\t< Prev\tassorted scents\tbright citrus\tcalming lavender\tginger fresh\tsimply non-scents\ttravel set (4-pack)\t3 ounce (pack of 1)\t3-ounce (2-pack)\tDescription\tFeatures\tReviews\tBuy Now]

Action: click[Buy Now]
"""