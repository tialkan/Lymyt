#include <cassert>
#include "../firmware/Lymyt/Learning.h"

int main() {
  Learning state;
  assert(state.press(24));
  assert(state.words);
  assert(!state.press(24)); // E-paper still pending: don't skip an unseen card.
  assert(state.index == 0 && state.learned == 0);
  state.displayed();
  assert(state.press(24));
  assert(!state.words && state.index == 1 && state.learned == 1);
  assert(!state.press(24));
  state.displayed();
  assert(state.press(24));
  state.displayed();
  assert(state.index == 1 && state.learned == 1);
  assert(state.press(24));
  assert(state.index == 2 && state.learned == 3);
  Learning last;
  last.words = last.displayedWords = true;
  last.index = 23;
  assert(last.press(24));
  assert(last.index == 0 && last.learned == (1u << 23));
}
