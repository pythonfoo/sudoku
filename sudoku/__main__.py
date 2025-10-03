# from .field import Field


# field = Field(
#     # "123456789789123456456789123512647938934815267867932514248371695395264871671598342"
#     "800000503501007000700308210680073000009005000300004805970500680063789000150040007"
# )
# actions = field.show_possibles()
# field.apply(actions)
# field.set_cell(1, 0, 9)
# actions = field.show_possibles()
# for action in actions:
#     print(action)
# # print(repr(field.get_cell(1, 0)))
# # field.set_cell(1, 0, 9)

# # print(field)


from .pg_gui.game import main

# from .text_ui.game import main

main()
