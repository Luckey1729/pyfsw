from flask import redirect, render_template, url_for, request, flash
from time import time

from pyfsw import app, db
from pyfsw import Player, ShopCategory, ShopItem, ShopOrder
from pyfsw import login_required, current_user

@app.route('/shop/offer')
def route_shop():
	categories = db.session.query(ShopCategory).all()
	return render_template('shop/browse.htm', categories=categories, logged=current_user())

@app.route('/shop/order/<int:id>', methods=['GET'])
@login_required
def route_shop_order(id):
	item = db.session.query(ShopItem).filter(ShopItem.id == id).first()
	if not item or not item.enabled:
		return redirect(url_for('route_shop'))

	characters = current_user().players
	return render_template('shop/order.htm', item=item, characters=characters)

@app.route('/shop/order/<int:id>', methods=['POST'])
@login_required
def route_shop_order_post(id):
	item = request.form.get('item', 0, type=int)
	character = request.form.get('character', 0, type=int)
	order = True

	if item == 0 or character == 0:
		return redirect(url_for('route_shop'))

	item = db.session().query(ShopItem).filter(ShopItem.id == item).first()
	if not item:
		flash('Failed to find the selected item.')

	character = db.session().query(Player).filter(Player.id == character).first()
	if not character:
		order = False
		flash('Failed to find the selected character.')

	account = current_user()
	if character not in account.players:
		order = False
		flash('You can not order an item for foreign character.')

	if account.points < item.price:
		order = False
		flash('You do not have enough premium points to purchase this item.')

	if order:
		order = ShopOrder()
		order.name = item.name
		order.type = item.type
		order.key = item.key
		order.value = item.value
		order.price = item.price
		order.ordered = int(time())
		order.character_id = character.id

		account.points -= item.price

		db.session().add(order)
		db.session().commit()

		flash('The item has been ordered and should be delivered soon to your character.')

	return redirect(url_for('route_shop'))
