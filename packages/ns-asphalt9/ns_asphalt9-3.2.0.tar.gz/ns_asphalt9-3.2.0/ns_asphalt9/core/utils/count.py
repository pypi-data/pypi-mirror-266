from .. import consts


class CountManager:
    def __init__(self):
        self.init_data()

    def race_count_inc(self, mode):
        self.race_count[mode] += 1

    def get_race_count(self, mode):
        return self.race_count[mode]

    def total_race_count_inc(self):
        self.total_race_count += 1

    def race_rank_inc(self, mode, rank):
        self.race_rank[mode][rank] += 1

    def get_race_rank(self, mode):
        return self.race_rank[mode]

    def track_rank_inc(self, mode, track, rank):
        if track not in self.track_rank[mode]:
            self.track_rank[mode][track] = {rank: 0}
            if rank not in self.track_rank[mode][track]:
                self.track_rank[mode][track][rank] = 0
        self.track_rank[mode][track][rank] += 1

    def get_track_rank(self, mode):
        return self.track_rank[mode]

    def not_support_track_inc(self, track):
        if track not in self.not_support_track:
            self.not_support_track.append(track)

    def not_recongnized_track_inc(self, track):
        if track not in self.not_recongnized_track:
            self.not_recongnized_track.append(track)

    def init_data(self):
        self.total_race_count = 0
        self.race_count = {
            consts.mp1_zh: 0,
            consts.mp2_zh: 0,
            consts.mp3_zh: 0,
            consts.car_hunt_zh: 0,
            consts.legendary_hunt_zh: 0,
            consts.custom_event_zh: 0,
            consts.career_zh: 0,
        }

        self.race_rank = {
            consts.mp1_zh: {i: 0 for i in range(1, 9)},
            consts.mp2_zh: {i: 0 for i in range(1, 9)},
            consts.mp3_zh: {i: 0 for i in range(1, 9)},
            consts.car_hunt_zh: {i: 0 for i in range(1, 5)},
            consts.legendary_hunt_zh: {i: 0 for i in range(1, 5)},
            consts.custom_event_zh: {i: 0 for i in range(1, 9)},
            consts.career_zh: {i: 0 for i in range(1, 9)},
        }

        self.track_rank = {
            consts.mp1_zh: {},
            consts.mp2_zh: {},
            consts.mp3_zh: {},
            consts.car_hunt_zh: {},
            consts.legendary_hunt_zh: {},
            consts.custom_event_zh: {},
            consts.career_zh: {},
        }

        # Not Support Track
        self.not_support_track = []

        # Not Recongnized Track
        self.not_recongnized_track = []


count = CountManager()
