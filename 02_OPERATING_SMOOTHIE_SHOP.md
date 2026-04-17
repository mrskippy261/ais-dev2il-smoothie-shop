# DEV2IL: Observability

## The Smoothie Shop

The smoothie shop application allows users to order delicious smoothies. It consists of two microservices:
- The Order Service: Accepts smoothie orders
- The Kitchen Service: Prepares the smoothies

![Smoothie Shop](smoothie-shop.png)

To open your personal smoothie shop
- Open a terminal and run `uv run uvicorn order_service:app --port 8000 --reload`. 
- Open another terminal and run: `uv run uvicorn kitchen_service:app --port 8001 --reload`.

## Operating the Smoothie Shop in Blind Mode

Let's start to buy some smoothies. Open a terminal and run `uv run buy_smoothies.py`. 
Look at the console output. You should see that your smoothie shop is working fine.

Let's start to send some more customers to your smoothie shop. Open another terminal and run 
`uv run buy_smoothies.py`. Look at the console output again.

It looks like your shop is having some troubles from time to time. Try to figure out what is going wrong by
looking at the outputs of all the started services. **You are not allowed to look at the code!** 
Could you figure it out and fix it ?

Most likely, you've been unable to tell why the application failed from time to time. The only way to 
find out is to ask the developers. If you look into the code of `kitchen_service.py`, you will notice
that the kitchen rejects a request to prepare a smoothie with a status code of 503 if all cooks are
so busy that the work on the requested smoothie can't be started in time. In this case, the fix would 
have been easy, as the kitchen already contains a configuration parameter to increase the number of cooks
(`NUM_COOKS`).
