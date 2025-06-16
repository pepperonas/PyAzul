import tkinter as tk
from tkinter import ttk, messagebox
import random
from enum import Enum
from typing import List, Optional, Tuple
import math


class TileColor(Enum):
	"""Die 5 Fliesenfarben im Spiel"""
	BLUE = "#0066CC"
	YELLOW = "#FFD700"
	RED = "#CC0000"
	BLACK = "#2C2E3B"
	WHITE = "#E0E0E0"


class GamePhase(Enum):
	"""Spielphasen"""
	PATTERN = "Musterphase"
	TILING = "Fliesungsphase"
	PREPARATION = "Vorbereitung"
	GAME_END = "Spielende"


class Tile:
	"""Repräsentiert eine einzelne Fliese"""

	def __init__(self, color: TileColor):
		self.color = color


class Factory:
	"""Manufakturplättchen"""

	def __init__(self):
		self.tiles: List[Tile] = []

	def add_tiles(self, tiles: List[Tile]):
		self.tiles.extend(tiles)

	def take_color(self, color: TileColor) -> Tuple[List[Tile], List[Tile]]:
		"""Nimmt alle Fliesen einer Farbe, gibt (genommene, übrige) zurück"""
		taken = [t for t in self.tiles if t.color == color]
		remaining = [t for t in self.tiles if t.color != color]
		self.tiles.clear()
		return taken, remaining


class WallPattern:
	"""Das Wandmuster - 5x5 Grid mit festem Farbmuster"""
	# Festes Muster wie auf der Spielerablage
	PATTERN = [
		[TileColor.BLUE, TileColor.YELLOW, TileColor.RED, TileColor.BLACK, TileColor.WHITE],
		[TileColor.WHITE, TileColor.BLUE, TileColor.YELLOW, TileColor.RED, TileColor.BLACK],
		[TileColor.BLACK, TileColor.WHITE, TileColor.BLUE, TileColor.YELLOW, TileColor.RED],
		[TileColor.RED, TileColor.BLACK, TileColor.WHITE, TileColor.BLUE, TileColor.YELLOW],
		[TileColor.YELLOW, TileColor.RED, TileColor.BLACK, TileColor.WHITE, TileColor.BLUE]
	]


class PlayerBoard:
	"""Spielerablage mit Musterreihen, Wand und Bodenreihe"""

	def __init__(self):
		self.pattern_lines = [[] for _ in range(5)]  # 5 Musterreihen (1-5 Plätze)
		self.wall = [[None for _ in range(5)] for _ in range(5)]  # 5x5 Wand
		self.floor_line = []  # Bodenreihe
		self.score = 0
		self.has_first_player_marker = False

	def can_add_to_pattern_line(self, line_idx: int, color: TileColor) -> bool:
		"""Prüft ob Fliesen in eine Musterreihe gelegt werden können"""
		if line_idx < 0 or line_idx >= 5:
			return False

		pattern_line = self.pattern_lines[line_idx]
		max_tiles = line_idx + 1

		# Reihe voll?
		if len(pattern_line) >= max_tiles:
			return False

		# Reihe leer oder gleiche Farbe?
		if pattern_line and pattern_line[0].color != color:
			return False

		# Farbe bereits in der Wandreihe?
		wall_row = self.wall[line_idx]
		wall_colors = [WallPattern.PATTERN[line_idx][i] for i, tile in enumerate(wall_row) if tile is not None]
		if color in wall_colors:
			return False

		return True

	def add_to_pattern_line(self, line_idx: int, tiles: List[Tile]) -> List[Tile]:
		"""Fügt Fliesen zu Musterreihe hinzu, gibt überschüssige zurück"""
		if not tiles:
			return []

		max_tiles = line_idx + 1
		current_tiles = len(self.pattern_lines[line_idx])
		space_left = max_tiles - current_tiles

		tiles_to_add = tiles[:space_left]
		overflow = tiles[space_left:]

		self.pattern_lines[line_idx].extend(tiles_to_add)
		return overflow

	def add_to_floor_line(self, tiles: List[Tile]):
		"""Fügt Fliesen zur Bodenreihe hinzu"""
		self.floor_line.extend(tiles)

	def score_floor_line(self):
		"""Berechnet Minuspunkte für Bodenreihe"""
		penalties = [-1, -1, -2, -2, -2, -3, -3]

		for i, tile in enumerate(self.floor_line[:7]):
			if i < len(penalties):
				self.score = max(0, self.score + penalties[i])

		# Startspielermarker zählt auch als -1
		if self.has_first_player_marker:
			self.score = max(0, self.score - 1)

	def move_complete_lines_to_wall(self) -> List[Tile]:
		"""Bewegt komplette Musterreihen zur Wand, gibt entfernte Fliesen zurück"""
		removed_tiles = []

		for i in range(5):
			line = self.pattern_lines[i]
			if len(line) == i + 1:  # Reihe komplett
				# Nimm rechte Fliese (letzte)
				tile = line[-1]

				# Finde Position in der Wand
				for j in range(5):
					if WallPattern.PATTERN[i][j] == tile.color:
						self.wall[i][j] = tile
						self.score += self._calculate_tile_score(i, j)
						break

				# Entferne restliche Fliesen
				removed_tiles.extend(line[:-1])
				self.pattern_lines[i] = []

		return removed_tiles

	def _calculate_tile_score(self, row: int, col: int) -> int:
		"""Berechnet Punkte für neu gesetzte Fliese"""
		score = 0

		# Horizontale Gruppe
		h_start = col
		while h_start > 0 and self.wall[row][h_start - 1]:
			h_start -= 1

		h_end = col
		while h_end < 4 and self.wall[row][h_end + 1]:
			h_end += 1

		h_count = h_end - h_start + 1
		if h_count > 1:
			score += h_count

		# Vertikale Gruppe
		v_start = row
		while v_start > 0 and self.wall[v_start - 1][col]:
			v_start -= 1

		v_end = row
		while v_end < 4 and self.wall[v_end + 1][col]:
			v_end += 1

		v_count = v_end - v_start + 1
		if v_count > 1:
			score += v_count

		# Einzelne Fliese
		if h_count == 1 and v_count == 1:
			score = 1

		return score

	def calculate_end_game_bonus(self) -> int:
		"""Berechnet Endspiel-Bonuspunkte"""
		bonus = 0

		# Horizontale Reihen (2 Punkte pro vollständiger Reihe)
		for row in self.wall:
			if all(tile is not None for tile in row):
				bonus += 2

		# Vertikale Reihen (7 Punkte pro vollständiger Reihe)
		for col in range(5):
			if all(self.wall[row][col] is not None for row in range(5)):
				bonus += 7

		# Alle 5 Fliesen einer Farbe (10 Punkte)
		for color in TileColor:
			count = 0
			for row in range(5):
				for col in range(5):
					if self.wall[row][col] and WallPattern.PATTERN[row][col] == color:
						count += 1
			if count == 5:
				bonus += 10

		return bonus

	def has_complete_row(self) -> bool:
		"""Prüft ob eine horizontale Reihe vollständig ist"""
		return any(all(tile is not None for tile in row) for row in self.wall)


class AzulGame:
	"""Hauptspiellogik"""

	def __init__(self, num_players: int):
		self.num_players = num_players
		self.players = [PlayerBoard() for _ in range(num_players)]
		self.current_player = 0
		self.phase = GamePhase.PATTERN
		self.first_player_marker_taken = False

		# Manufakturen
		factory_count = {2: 5, 3: 7, 4: 9}[num_players]
		self.factories = [Factory() for _ in range(factory_count)]
		self.center = []  # Tischmitte

		# Fliesenbeutel
		self.bag = []
		self.discarded = []
		self._fill_bag()

		# Fliesen auf Manufakturen verteilen
		self._refill_factories()

	def _fill_bag(self):
		"""Füllt den Beutel mit 100 Fliesen (20 pro Farbe)"""
		for color in TileColor:
			self.bag.extend([Tile(color) for _ in range(20)])
		random.shuffle(self.bag)

	def _refill_factories(self):
		"""Bestückt jedes Manufakturplättchen mit 4 Fliesen"""
		for factory in self.factories:
			tiles_needed = 4
			while tiles_needed > 0 and (self.bag or self.discarded):
				if not self.bag:
					self.bag = self.discarded
					self.discarded = []
					random.shuffle(self.bag)

				if self.bag:
					tiles_to_add = min(tiles_needed, len(self.bag))
					factory.add_tiles(self.bag[:tiles_to_add])
					self.bag = self.bag[tiles_to_add:]
					tiles_needed -= tiles_to_add

	def get_available_colors_factory(self, factory_idx: int) -> List[TileColor]:
		"""Gibt verfügbare Farben einer Manufaktur zurück"""
		if factory_idx < 0 or factory_idx >= len(self.factories):
			return []
		return list(set(t.color for t in self.factories[factory_idx].tiles))

	def get_available_colors_center(self) -> List[TileColor]:
		"""Gibt verfügbare Farben aus der Mitte zurück"""
		return list(set(t.color for t in self.center))

	def take_from_factory(self, player_idx: int, factory_idx: int, color: TileColor, pattern_line_idx: int):
		"""Spieler nimmt Fliesen von Manufaktur"""
		if player_idx != self.current_player:
			return False

		factory = self.factories[factory_idx]
		taken, remaining = factory.take_color(color)

		if not taken:
			return False

		# Übrige Fliesen in die Mitte
		self.center.extend(remaining)

		# Fliesen platzieren
		self._place_tiles(player_idx, taken, pattern_line_idx)
		self._next_turn()
		return True

	def take_from_center(self, player_idx: int, color: TileColor, pattern_line_idx: int):
		"""Spieler nimmt Fliesen aus der Mitte"""
		if player_idx != self.current_player:
			return False

		taken = [t for t in self.center if t.color == color]
		self.center = [t for t in self.center if t.color != color]

		if not taken:
			return False

		# Startspielermarker
		if not self.first_player_marker_taken:
			self.players[player_idx].has_first_player_marker = True
			self.first_player_marker_taken = True

		# Fliesen platzieren
		self._place_tiles(player_idx, taken, pattern_line_idx)
		self._next_turn()
		return True

	def _place_tiles(self, player_idx: int, tiles: List[Tile], pattern_line_idx: int):
		"""Platziert Fliesen auf Spielerablage"""
		player = self.players[player_idx]

		if pattern_line_idx == -1:  # Direkt in Bodenreihe
			player.add_to_floor_line(tiles)
		else:
			overflow = player.add_to_pattern_line(pattern_line_idx, tiles)
			if overflow:
				player.add_to_floor_line(overflow)

	def _next_turn(self):
		"""Wechselt zum nächsten Spieler oder Phase"""
		# Prüfe ob Musterphase beendet
		if not any(f.tiles for f in self.factories) and not self.center:
			self._start_tiling_phase()
		else:
			self.current_player = (self.current_player + 1) % self.num_players

	def _start_tiling_phase(self):
		"""Startet Fliesungsphase"""
		self.phase = GamePhase.TILING

		for player in self.players:
			# Verschiebe komplette Reihen zur Wand
			removed = player.move_complete_lines_to_wall()
			self.discarded.extend(removed)

			# Werte Bodenreihe
			player.score_floor_line()
			self.discarded.extend(player.floor_line)
			player.floor_line = []

		# Prüfe Spielende
		if any(p.has_complete_row() for p in self.players):
			self._end_game()
		else:
			self._prepare_next_round()

	def _prepare_next_round(self):
		"""Bereitet nächste Runde vor"""
		self.phase = GamePhase.PREPARATION

		# Startspieler für nächste Runde
		for i, player in enumerate(self.players):
			if player.has_first_player_marker:
				self.current_player = i
				player.has_first_player_marker = False
				break

		self.first_player_marker_taken = False
		self._refill_factories()
		self.phase = GamePhase.PATTERN

	def _end_game(self):
		"""Beendet das Spiel und berechnet Endwertung"""
		self.phase = GamePhase.GAME_END

		for player in self.players:
			player.score += player.calculate_end_game_bonus()


class AzulGUI:
	"""Grafische Benutzeroberfläche für Azul"""

	def __init__(self, root):
		self.root = root
		self.root.title("Azul")
		self.root.configure(bg="#2C2E3B")

		# Spieleranzahl-Dialog
		self.num_players = self._ask_player_count()

		# Spiel initialisieren
		self.game = AzulGame(self.num_players)
		
		# Spielernamen
		self.player_names = [f"Spieler {i+1}" for i in range(self.num_players)]

		# GUI-Variablen
		self.selected_factory = None
		self.selected_color = None
		self.selected_pattern_line = None

		# Hauptframe
		self.main_frame = ttk.Frame(root, style="Dark.TFrame")
		self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

		# Styles konfigurieren
		self._configure_styles()

		# GUI aufbauen
		self._build_gui()

		# Spiel starten
		self._update_display()

	def _ask_player_count(self):
		"""Dialog für Spieleranzahl"""
		dialog = tk.Toplevel(self.root)
		dialog.title("Spieleranzahl")
		dialog.configure(bg="#2C2E3B")
		dialog.geometry("300x150")

		# Zentrieren
		dialog.transient(self.root)
		dialog.grab_set()

		tk.Label(dialog, text="Anzahl Spieler:", bg="#2C2E3B", fg="white",
		         font=("Arial", 14)).pack(pady=20)

		result = tk.IntVar(value=2)

		button_frame = tk.Frame(dialog, bg="#2C2E3B")
		button_frame.pack()

		for i in range(2, 5):
			tk.Button(button_frame, text=str(i), width=5, height=2,
			          bg="#4A4C5B", fg="black", font=("Arial", 12),
			          command=lambda x=i: [result.set(x), dialog.destroy()]).pack(side=tk.LEFT, padx=5)

		dialog.wait_window()
		return result.get()

	def _configure_styles(self):
		"""Konfiguriert ttk Styles"""
		style = ttk.Style()
		style.theme_use('clam')

		# Dark theme
		style.configure("Dark.TFrame", background="#2C2E3B")
		style.configure("Dark.TLabel", background="#2C2E3B", foreground="white")
		style.configure("Dark.TButton", background="#4A4C5B", foreground="black")
		style.map("Dark.TButton",
		          background=[('active', '#5A5C6B'), ('pressed', '#3A3C4B')])

	def _build_gui(self):
		"""Baut die GUI auf"""
		# Oberer Bereich: Spielinfo
		info_frame = ttk.Frame(self.main_frame, style="Dark.TFrame")
		info_frame.grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0, 20))

		self.phase_label = ttk.Label(info_frame, text="", style="Dark.TLabel", font=("Arial", 16, "bold"))
		self.phase_label.pack()

		self.current_player_label = ttk.Label(info_frame, text="", style="Dark.TLabel", font=("Arial", 14))
		self.current_player_label.pack()

		# Linker Bereich: Manufakturen und Tischmitte
		factory_frame = ttk.Frame(self.main_frame, style="Dark.TFrame")
		factory_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 20))

		ttk.Label(factory_frame, text="Manufakturen", style="Dark.TLabel",
		          font=("Arial", 14, "bold")).pack(pady=(0, 10))

		self.factory_widgets = []
		for i in range(len(self.game.factories)):
			factory_widget = self._create_factory_widget(factory_frame, i)
			factory_widget["frame"].pack(pady=5)
			self.factory_widgets.append(factory_widget)

		# Tischmitte
		ttk.Label(factory_frame, text="Tischmitte", style="Dark.TLabel",
		          font=("Arial", 14, "bold")).pack(pady=(20, 10))

		self.center_widget = self._create_center_widget(factory_frame)
		self.center_widget["frame"].pack(pady=5)

		# Rechter Bereich: Spielerablagen
		players_frame = ttk.Frame(self.main_frame, style="Dark.TFrame")
		players_frame.grid(row=1, column=1, sticky="nsew")

		self.player_widgets = []
		for i in range(self.num_players):
			player_widget = self._create_player_widget(players_frame, i)
			player_widget["frame"].grid(row=i // 2, column=i % 2, padx=10, pady=10)
			self.player_widgets.append(player_widget)

		# Grid-Gewichte
		self.main_frame.columnconfigure(1, weight=1)
		self.main_frame.rowconfigure(1, weight=1)

	def _create_factory_widget(self, parent, factory_idx):
		"""Erstellt Widget für eine Manufaktur"""
		frame = tk.Frame(parent, bg="#4A4C5B", relief=tk.RAISED, bd=2)

		canvas = tk.Canvas(frame, width=120, height=120, bg="#5A5C6B", highlightthickness=0)
		canvas.pack(padx=5, pady=5)

		# Click-Handler
		canvas.bind("<Button-1>", lambda e: self._on_factory_click(factory_idx))

		return {"frame": frame, "canvas": canvas}

	def _create_center_widget(self, parent):
		"""Erstellt Widget für Tischmitte"""
		frame = tk.Frame(parent, bg="#3A3C4B", relief=tk.SUNKEN, bd=2)

		canvas = tk.Canvas(frame, width=200, height=150, bg="#4A4C5B", highlightthickness=0)
		canvas.pack(padx=5, pady=5)

		# Click-Handler
		canvas.bind("<Button-1>", lambda e: self._on_center_click())

		return {"frame": frame, "canvas": canvas}

	def _create_player_widget(self, parent, player_idx):
		"""Erstellt Widget für Spielerablage"""
		frame = tk.Frame(parent, bg="#3A3C4B", relief=tk.RAISED, bd=3)

		# Spielername und Punkte
		header = tk.Frame(frame, bg="#3A3C4B")
		header.pack(fill=tk.X, padx=5, pady=5)

		name_entry = tk.Entry(header, width=12, font=("Arial", 12, "bold"),
		                      bg="#4A4C5B", fg="white", insertbackground="white")
		name_entry.insert(0, f"Spieler {player_idx + 1}")
		name_entry.bind('<Return>', lambda e: self._update_player_name(player_idx, name_entry.get()))
		name_entry.bind('<FocusOut>', lambda e: self._update_player_name(player_idx, name_entry.get()))
		name_entry.pack(side=tk.LEFT)

		score_label = tk.Label(header, text="0 Punkte",
		                       bg="#3A3C4B", fg="#FFD700", font=("Arial", 12))
		score_label.pack(side=tk.RIGHT)

		# Musterreihen
		pattern_frame = tk.Frame(frame, bg="#3A3C4B")
		pattern_frame.pack(pady=5)

		tk.Label(pattern_frame, text="Musterreihen", bg="#3A3C4B", fg="white",
		         font=("Arial", 10)).grid(row=0, column=0, columnspan=2)

		pattern_canvases = []
		for i in range(5):
			canvas = tk.Canvas(pattern_frame, width=30 * (i + 1), height=30,
			                   bg="#5A5C6B", highlightthickness=1, highlightbackground="white")
			canvas.grid(row=i + 1, column=0, padx=5, pady=2)
			canvas.bind("<Button-1>", lambda e, idx=i: self._on_pattern_line_click(player_idx, idx))
			pattern_canvases.append(canvas)

		# Wand
		wall_frame = tk.Frame(frame, bg="#3A3C4B")
		wall_frame.pack(pady=5)

		tk.Label(wall_frame, text="Wand", bg="#3A3C4B", fg="white",
		         font=("Arial", 10)).pack()

		wall_canvas = tk.Canvas(wall_frame, width=150, height=150, bg="#4A4C5B", highlightthickness=0)
		wall_canvas.pack()

		# Bodenreihe
		floor_frame = tk.Frame(frame, bg="#3A3C4B")
		floor_frame.pack(pady=5)

		tk.Label(floor_frame, text="Bodenreihe", bg="#3A3C4B", fg="white",
		         font=("Arial", 10)).pack()

		floor_canvas = tk.Canvas(floor_frame, width=210, height=30, bg="#5A5C6B", highlightthickness=0)
		floor_canvas.pack()

		return {
			"frame": frame,
			"name_entry": name_entry,
			"score_label": score_label,
			"pattern_canvases": pattern_canvases,
			"wall_canvas": wall_canvas,
			"floor_canvas": floor_canvas
		}

	def _update_player_name(self, player_idx, new_name):
		"""Aktualisiert den Namen eines Spielers"""
		if new_name.strip():
			self.player_names[player_idx] = new_name.strip()
			self._update_display()

	def _draw_tile(self, canvas, x, y, color: TileColor, size=25):
		"""Zeichnet eine einzelne Fliese"""
		canvas.create_rectangle(x, y, x + size, y + size,
		                        fill=color.value, outline="black", width=2)

	def _update_display(self):
		"""Aktualisiert die gesamte Anzeige"""
		# Phase und aktueller Spieler
		self.phase_label.config(text=f"Phase: {self.game.phase.value}")
		if self.game.phase == GamePhase.PATTERN:
			current_player_name = self.player_names[self.game.current_player]
			self.current_player_label.config(text=f"{current_player_name} ist am Zug")
		else:
			self.current_player_label.config(text="")

		# Manufakturen
		for i, factory_widget in enumerate(self.factory_widgets):
			canvas = factory_widget["canvas"]
			canvas.delete("all")

			factory = self.game.factories[i]
			if factory.tiles:
				# Fliesen im 2x2 Grid anordnen
				positions = [(30, 30), (65, 30), (30, 65), (65, 65)]
				for j, tile in enumerate(factory.tiles[:4]):
					x, y = positions[j]
					self._draw_tile(canvas, x, y, tile.color)

		# Tischmitte
		canvas = self.center_widget["canvas"]
		canvas.delete("all")

		if self.game.center:
			# Fliesen gruppiert nach Farbe anzeigen
			color_groups = {}
			for tile in self.game.center:
				if tile.color not in color_groups:
					color_groups[tile.color] = 0
				color_groups[tile.color] += 1

			x_offset = 10
			for color, count in color_groups.items():
				self._draw_tile(canvas, x_offset, 10, color, 30)
				canvas.create_text(x_offset + 15, 50, text=str(count),
				                   fill="white", font=("Arial", 12, "bold"))
				x_offset += 40

		# Startspielermarker
		if not self.game.first_player_marker_taken and self.game.phase == GamePhase.PATTERN:
			canvas.create_text(100, 120, text="1", fill="white",
			                   font=("Arial", 16, "bold"))

		# Spielerablagen
		for i, player_widget in enumerate(self.player_widgets):
			player = self.game.players[i]

			# Punkte
			player_widget["score_label"].config(text=f"{player.score} Punkte")

			# Musterreihen
			for j, canvas in enumerate(player_widget["pattern_canvases"]):
				canvas.delete("all")
				line = player.pattern_lines[j]
				for k, tile in enumerate(line):
					self._draw_tile(canvas, k * 30 + 2, 2, tile.color, 26)

			# Wand
			canvas = player_widget["wall_canvas"]
			canvas.delete("all")

			# Zeichne Wandmuster
			for row in range(5):
				for col in range(5):
					x, y = col * 30, row * 30
					color = WallPattern.PATTERN[row][col]

					if player.wall[row][col]:
						# Fliese gesetzt
						self._draw_tile(canvas, x, y, color)
					else:
						# Leeres Feld mit Farbindikator
						canvas.create_rectangle(x, y, x + 30, y + 30,
						                        fill="#6A6C7B", outline="white")
						canvas.create_rectangle(x + 10, y + 10, x + 20, y + 20,
						                        fill=color.value, outline="")

			# Bodenreihe
			canvas = player_widget["floor_canvas"]
			canvas.delete("all")

			penalties = ["-1", "-1", "-2", "-2", "-2", "-3", "-3"]
			for j in range(7):
				x = j * 30
				canvas.create_rectangle(x, 0, x + 30, 30, fill="#5A5C6B", outline="white")
				canvas.create_text(x + 15, 15, text=penalties[j], fill="white", font=("Arial", 8))

			for j, tile in enumerate(player.floor_line[:7]):
				if j < 7:
					self._draw_tile(canvas, j * 30 + 2, 2, tile.color, 26)

			# Startspielermarker
			if player.has_first_player_marker:
				canvas.create_text(15, 15, text="1", fill="white",
				                   font=("Arial", 12, "bold"))

		# Prüfe auf Spielende
		if self.game.phase == GamePhase.GAME_END:
			self._show_game_end()

	def _on_factory_click(self, factory_idx):
		"""Handler für Klick auf Manufaktur"""
		if self.game.phase != GamePhase.PATTERN:
			return

		colors = self.game.get_available_colors_factory(factory_idx)
		if not colors:
			return

		self.selected_factory = factory_idx
		self.selected_color = self._ask_color_choice(colors)

		if self.selected_color:
			self._ask_pattern_line()

	def _on_center_click(self):
		"""Handler für Klick auf Tischmitte"""
		if self.game.phase != GamePhase.PATTERN:
			return

		colors = self.game.get_available_colors_center()
		if not colors:
			return

		self.selected_factory = -1  # -1 für Tischmitte
		self.selected_color = self._ask_color_choice(colors)

		if self.selected_color:
			self._ask_pattern_line()

	def _on_pattern_line_click(self, player_idx, pattern_line_idx):
		"""Handler für Klick auf Musterreihe"""
		if player_idx != self.game.current_player:
			return

		if self.selected_color and self.selected_factory is not None:
			self._place_tiles(pattern_line_idx)

	def _ask_color_choice(self, colors: List[TileColor]):
		"""Dialog für Farbauswahl"""
		if len(colors) == 1:
			return colors[0]

		dialog = tk.Toplevel(self.root)
		dialog.title("Farbe wählen")
		dialog.configure(bg="#2C2E3B")
		dialog.transient(self.root)
		dialog.grab_set()

		tk.Label(dialog, text="Welche Farbe möchtest du nehmen?",
		         bg="#2C2E3B", fg="white", font=("Arial", 12)).pack(pady=10)

		result = None

		button_frame = tk.Frame(dialog, bg="#2C2E3B")
		button_frame.pack(pady=10)

		def choose_color(color):
			nonlocal result
			result = color
			dialog.destroy()

		for color in colors:
			# Canvas als farbiger Button
			canvas = tk.Canvas(button_frame, width=80, height=40, 
			                  bg=color.value, highlightthickness=2, highlightbackground="white")
			canvas.create_rectangle(2, 2, 78, 38, fill=color.value, outline="black", width=2)
			canvas.bind("<Button-1>", lambda e, c=color: choose_color(c))
			canvas.pack(side=tk.LEFT, padx=5)

		dialog.wait_window()
		return result

	def _ask_pattern_line(self):
		"""Dialog für Musterreihenauswahl"""
		player = self.game.players[self.game.current_player]

		# Prüfe verfügbare Reihen
		available_lines = []
		for i in range(5):
			if player.can_add_to_pattern_line(i, self.selected_color):
				available_lines.append(i)

		dialog = tk.Toplevel(self.root)
		dialog.title("Musterreihe wählen")
		dialog.configure(bg="#2C2E3B")
		dialog.transient(self.root)
		dialog.grab_set()

		tk.Label(dialog, text="In welche Reihe möchtest du die Fliesen legen?",
		         bg="#2C2E3B", fg="white", font=("Arial", 12)).pack(pady=10)

		button_frame = tk.Frame(dialog, bg="#2C2E3B")
		button_frame.pack(pady=10)

		def choose_line(line_idx):
			self._place_tiles(line_idx)
			dialog.destroy()

		# Verfügbare Musterreihen
		for i in available_lines:
			btn = tk.Button(button_frame, text=f"Reihe {i + 1}", width=10,
			                bg="#4A4C5B", fg="black", font=("Arial", 10),
			                command=lambda idx=i: choose_line(idx))
			btn.pack(pady=2)

		# Bodenreihe Option
		tk.Button(button_frame, text="Bodenreihe", width=10,
		          bg="#8B4513", fg="black", font=("Arial", 10),
		          command=lambda: choose_line(-1)).pack(pady=5)

		dialog.wait_window()

	def _place_tiles(self, pattern_line_idx):
		"""Platziert ausgewählte Fliesen"""
		if self.selected_factory == -1:  # Tischmitte
			success = self.game.take_from_center(self.game.current_player,
			                                     self.selected_color, pattern_line_idx)
		else:
			success = self.game.take_from_factory(self.game.current_player,
			                                      self.selected_factory,
			                                      self.selected_color, pattern_line_idx)

		if success:
			self.selected_factory = None
			self.selected_color = None
			self._update_display()

	def _show_game_end(self):
		"""Zeigt Spielende-Dialog"""
		# Finde Gewinner
		max_score = max(p.score for p in self.game.players)
		winners = [i for i, p in enumerate(self.game.players) if p.score == max_score]

		if len(winners) == 1:
			winner_name = self.player_names[winners[0]]
			winner_text = f"{winner_name} gewinnt mit {max_score} Punkten!"
		else:
			winner_names = ", ".join(self.player_names[i] for i in winners)
			winner_text = f"Unentschieden! {winner_names} haben je {max_score} Punkte!"

		# Ergebnis-Dialog
		dialog = tk.Toplevel(self.root)
		dialog.title("Spielende")
		dialog.configure(bg="#2C2E3B")
		dialog.geometry("400x300")
		dialog.transient(self.root)
		dialog.grab_set()

		tk.Label(dialog, text="Spielende!", bg="#2C2E3B", fg="white",
		         font=("Arial", 20, "bold")).pack(pady=20)

		tk.Label(dialog, text=winner_text, bg="#2C2E3B", fg="#FFD700",
		         font=("Arial", 16)).pack(pady=10)

		# Punkteübersicht
		scores_frame = tk.Frame(dialog, bg="#2C2E3B")
		scores_frame.pack(pady=20)

		for i, player in enumerate(self.game.players):
			player_name = self.player_names[i]
			tk.Label(scores_frame, text=f"{player_name}: {player.score} Punkte",
			         bg="#2C2E3B", fg="white", font=("Arial", 12)).pack()

		tk.Button(dialog, text="Neues Spiel", bg="#4A4C5B", fg="black",
		          font=("Arial", 12), command=self._new_game).pack(pady=10)

		tk.Button(dialog, text="Beenden", bg="#8B4513", fg="black",
		          font=("Arial", 12), command=self.root.quit).pack()

	def _new_game(self):
		"""Startet ein neues Spiel"""
		self.root.destroy()
		root = tk.Tk()
		AzulGUI(root)
		root.mainloop()


def main():
	root = tk.Tk()
	game = AzulGUI(root)
	root.mainloop()


if __name__ == "__main__":
	main()