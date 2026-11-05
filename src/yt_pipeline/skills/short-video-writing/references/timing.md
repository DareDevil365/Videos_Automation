# Delivery and timing contract

Distinguish script rhythm from editing time. The writer chooses what a line changes and where the decisive thought ends. The editor measures complete speech and readable message holds. A text model cannot know a clip's final speech duration in advance.

The voiced chat editor places each complete exact-message clip 0.06 seconds after its bubble arrives. A notification already showing the message speaks it at that first preview instead: its screen extends through the full line, and the later bubble is not voiced twice. Each bubble hold is the maximum of measured speech plus a 0.26-second tail, the existing word/character reading heuristic, and a three-second attachment hold where needed. The final message receives another 0.65 seconds. Clips stay sequential. Other phone event screens occur before the next bubble/speech; returning to a conversation restores its own history. Names and timestamps are visual UI, not extra narration.

Initial typing delays are zero for the opening, 0.16 seconds for ordinary replies and 0.38 seconds before the final reply. These are defaults, not universal comic timing. Supported `chat_pause_before` overrides add 0-1.5 seconds before selected chat bubbles and preserve full speech/reading time; use them sparingly where the setup has created an expectation. A voiced notification already reveals the message and does not accept that extra bubble delay. Do not pad a weak story to its minimum length or truncate speech to fit the duration cap.

For comedy, protect the punchline's last thought and let the consequence register. For mystery, delay an answer only when the viewer has enough information to form a hypothesis. For emotional stories, let the character's choice carry the pause. A black screen is not automatically suspense. Music ducks under speech and fades around blackouts; blackouts remain silent. Distinct synthetic voices establish character identity but do not guarantee fear, sarcasm or dramatic acting.

Review actual exported timing and audio before calling an edit polished. Source/licensing checks, PCM peak checks and exact input text do not establish subjective naturalness or engagement.
