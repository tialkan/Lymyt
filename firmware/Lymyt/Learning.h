#pragma once
#include <stdint.h>

// A card is only acknowledged if that card has actually appeared on the display.
// This prevents queued e-paper taps from skipping invisible words.
struct Learning {
  bool words = false;
  bool displayedWords = false;
  bool pending = false;
  uint8_t index = 0;
  uint32_t learned = 0;

  bool press(unsigned count) {
    if (pending || !count) return false;
    if (words && displayedWords) {
      learned |= uint32_t(1) << index;
      index = (index + 1) % count;
    }
    words = !words;
    pending = true;
    return true;
  }
  void displayed() { displayedWords = words; pending = false; }
};
