"""
Fitness knowledge base — chunked documents for RAG indexing into Pinecone.
Each entry: { "id": str, "text": str, "metadata": { "category": str, "topic": str } }
"""

KNOWLEDGE_CHUNKS = [
    # ── EXERCISE TECHNIQUE ────────────────────────────────────────────────────
    {
        "id": "ex_001",
        "text": "Push-ups are a compound upper body exercise targeting the chest, triceps and anterior deltoids. "
                "Keep your body in a straight line from head to heels. Lower your chest to 2-3 cm from the floor, "
                "elbows at 45 degrees. Exhale on the way up. Beginners can start on knees. "
                "Common mistakes: sagging hips, flared elbows, incomplete range of motion.",
        "metadata": {"category": "exercise_technique", "topic": "push_up"},
    },
    {
        "id": "ex_002",
        "text": "Squats are the king of lower body exercises, targeting quadriceps, hamstrings, glutes and core. "
                "Stand feet shoulder-width apart, toes slightly out. Push hips back and down, "
                "keeping chest up and knees tracking over toes. Aim for thighs parallel to the floor. "
                "Drive through heels to stand. Keep spine neutral throughout.",
        "metadata": {"category": "exercise_technique", "topic": "squat"},
    },
    {
        "id": "ex_003",
        "text": "Deadlifts work the entire posterior chain — hamstrings, glutes, lower back, traps. "
                "Hinge at hips, keep the bar close to shins, flat back, chest up. "
                "Drive hips forward to stand tall. Never round the lower back under load. "
                "Start light to master form before adding weight.",
        "metadata": {"category": "exercise_technique", "topic": "deadlift"},
    },
    {
        "id": "ex_004",
        "text": "Pull-ups develop back width (latissimus dorsi) and biceps. "
                "Grip slightly wider than shoulder width, dead hang start. "
                "Pull chest to bar, elbows drive down and back. Lower with control. "
                "Assisted pull-ups or lat pulldowns are good progressions for beginners.",
        "metadata": {"category": "exercise_technique", "topic": "pull_up"},
    },
    {
        "id": "ex_005",
        "text": "Plank is an isometric core exercise. Keep body in a straight line from head to heels, "
                "elbows under shoulders. Engage core, glutes and quads simultaneously. "
                "Breathe normally. Aim to increase hold time progressively. "
                "Side plank targets the obliques specifically.",
        "metadata": {"category": "exercise_technique", "topic": "plank"},
    },
    {
        "id": "ex_006",
        "text": "Lunges improve single-leg strength, balance and hip flexibility. "
                "Step forward, lower back knee toward floor, front knee stays over ankle. "
                "Push through front heel to return. Reverse lunges are easier on the knees. "
                "Walking lunges add a cardiovascular element.",
        "metadata": {"category": "exercise_technique", "topic": "lunge"},
    },
    {
        "id": "ex_007",
        "text": "Overhead press targets shoulders (deltoids), triceps and upper traps. "
                "Press bar or dumbbells from shoulder height to fully extended overhead. "
                "Keep core braced, avoid excessive lower back arch. "
                "Seated variation reduces lower back strain for beginners.",
        "metadata": {"category": "exercise_technique", "topic": "overhead_press"},
    },
    {
        "id": "ex_008",
        "text": "Bent-over row builds mid-back thickness (rhomboids, mid traps, rear delts). "
                "Hinge forward at hips, spine neutral, pull bar or dumbbells to lower chest. "
                "Squeeze shoulder blades together at top. Control the descent. "
                "One-arm dumbbell row allows greater range of motion.",
        "metadata": {"category": "exercise_technique", "topic": "bent_over_row"},
    },

    # ── NUTRITION ─────────────────────────────────────────────────────────────
    {
        "id": "nut_001",
        "text": "Protein is essential for muscle repair and growth. "
                "Target 1.6–2.2 g per kg of bodyweight daily for active individuals. "
                "Best sources: chicken breast, eggs, Greek yogurt, lentils, tofu, fish. "
                "Spread protein intake across meals for optimal muscle protein synthesis.",
        "metadata": {"category": "nutrition", "topic": "protein"},
    },
    {
        "id": "nut_002",
        "text": "Carbohydrates are the primary fuel for high-intensity exercise. "
                "Complex carbs (oats, brown rice, sweet potato, quinoa) provide sustained energy. "
                "Simple carbs (fruit, white rice) are useful immediately post-workout for glycogen replenishment. "
                "Do not eliminate carbs for fat loss — reduce total calories instead.",
        "metadata": {"category": "nutrition", "topic": "carbohydrates"},
    },
    {
        "id": "nut_003",
        "text": "Healthy fats support hormone production, joint health and fat-soluble vitamin absorption. "
                "Include avocado, olive oil, nuts, seeds and fatty fish (salmon, mackerel). "
                "Aim for fats to make up 25–35% of total calories. "
                "Avoid trans fats found in processed and fried foods.",
        "metadata": {"category": "nutrition", "topic": "fats"},
    },
    {
        "id": "nut_004",
        "text": "Caloric deficit is required for fat loss. A deficit of 300–500 calories per day "
                "produces 0.3–0.5 kg of fat loss per week without excessive muscle loss. "
                "Larger deficits increase the risk of muscle loss and metabolic adaptation. "
                "Track calories for 2 weeks to establish your true maintenance level.",
        "metadata": {"category": "nutrition", "topic": "fat_loss"},
    },
    {
        "id": "nut_005",
        "text": "Caloric surplus is required for muscle gain. A surplus of 200–300 calories above maintenance "
                "minimises fat gain while supporting muscle growth (lean bulk). "
                "Prioritise protein at 2 g/kg bodyweight. "
                "Expect 0.5–1 kg total weight gain per month during a lean bulk.",
        "metadata": {"category": "nutrition", "topic": "muscle_gain"},
    },
    {
        "id": "nut_006",
        "text": "Hydration directly impacts exercise performance. Dehydration of just 2% of bodyweight "
                "reduces strength and endurance significantly. "
                "Aim for 35 ml per kg of bodyweight daily, more in hot weather or intense exercise. "
                "Urine colour is a simple hydration gauge — pale yellow is ideal.",
        "metadata": {"category": "nutrition", "topic": "hydration"},
    },
    {
        "id": "nut_007",
        "text": "Pre-workout nutrition: eat a mixed meal 2–3 hours before training (carbs + protein). "
                "If training within 1 hour, a small carb-rich snack (banana, rice cake) works well. "
                "Post-workout: consume protein within 2 hours of training to maximise muscle protein synthesis. "
                "30–40 g of protein with fast carbs is an effective post-workout combination.",
        "metadata": {"category": "nutrition", "topic": "meal_timing"},
    },

    # ── RECOVERY ──────────────────────────────────────────────────────────────
    {
        "id": "rec_001",
        "text": "Sleep is the most important recovery tool. 7–9 hours of quality sleep per night "
                "is required for muscle repair, hormone regulation (testosterone, growth hormone) "
                "and cognitive performance. Poor sleep increases cortisol, impairs recovery "
                "and increases injury risk. Prioritise consistent sleep and wake times.",
        "metadata": {"category": "recovery", "topic": "sleep"},
    },
    {
        "id": "rec_002",
        "text": "Active recovery on rest days improves blood flow and reduces muscle soreness (DOMS). "
                "Light walking, swimming, yoga or stretching for 20–30 minutes is ideal. "
                "Avoid high-intensity exercise on consecutive days for the same muscle groups. "
                "Most beginners benefit from 2 rest days per week.",
        "metadata": {"category": "recovery", "topic": "active_recovery"},
    },
    {
        "id": "rec_003",
        "text": "Delayed onset muscle soreness (DOMS) peaks 24–72 hours after exercise. "
                "It is caused by micro-tears in muscle fibres and is a normal adaptation response. "
                "Light movement, foam rolling, contrast showers and adequate protein help reduce DOMS. "
                "Severe pain (not soreness) in a joint or sharp pain during exercise requires medical attention.",
        "metadata": {"category": "recovery", "topic": "doms"},
    },
    {
        "id": "rec_004",
        "text": "Stretching improves flexibility and range of motion over time. "
                "Dynamic stretching (leg swings, arm circles) is best before exercise as a warm-up. "
                "Static stretching (holding 20–30 seconds) is best post-workout when muscles are warm. "
                "Yoga and mobility work 2–3 times per week significantly reduces injury risk.",
        "metadata": {"category": "recovery", "topic": "stretching"},
    },

    # ── TRAINING PRINCIPLES ───────────────────────────────────────────────────
    {
        "id": "tp_001",
        "text": "Progressive overload is the core principle of strength training. "
                "To build muscle and strength, you must continually increase the stimulus — "
                "more weight, more reps, more sets, or less rest over time. "
                "Track your workouts to ensure you are progressing each week.",
        "metadata": {"category": "training_principles", "topic": "progressive_overload"},
    },
    {
        "id": "tp_002",
        "text": "Training frequency matters for beginners and intermediates. "
                "Each muscle group should be trained 2–3 times per week for optimal hypertrophy. "
                "Full-body workouts 3x/week or upper/lower splits 4x/week work well. "
                "Advanced athletes may use more specialised splits.",
        "metadata": {"category": "training_principles", "topic": "frequency"},
    },
    {
        "id": "tp_003",
        "text": "Rep ranges and their purposes: 1–5 reps (heavy weight) builds maximal strength. "
                "6–12 reps (moderate weight) is optimal for hypertrophy (muscle growth). "
                "12–20+ reps (lighter weight) builds muscular endurance and can also contribute to hypertrophy. "
                "Varying rep ranges across a programme provides comprehensive adaptation.",
        "metadata": {"category": "training_principles", "topic": "rep_ranges"},
    },
    {
        "id": "tp_004",
        "text": "Warm-up before every session: 5 minutes light cardio + dynamic stretches + "
                "2–3 warm-up sets of your first exercise at 50–70% of working weight. "
                "Warm-up reduces injury risk, improves performance and primes the nervous system. "
                "Cool-down after: 5 minutes light cardio + static stretches.",
        "metadata": {"category": "training_principles", "topic": "warm_up"},
    },

    # ── SAFETY & INJURY PREVENTION ────────────────────────────────────────────
    {
        "id": "saf_001",
        "text": "Knee pain during squats or lunges is often caused by knees caving inward (valgus collapse). "
                "Focus on pushing knees out over toes. Strengthen glutes with hip thrusts and clamshells. "
                "If knee pain persists, reduce range of motion and consult a physiotherapist.",
        "metadata": {"category": "safety", "topic": "knee_pain"},
    },
    {
        "id": "saf_002",
        "text": "Lower back pain is frequently caused by poor form in deadlifts and squats — "
                "specifically rounding the lumbar spine under load. "
                "Always brace your core before lifting, maintain a neutral spine. "
                "If you experience sharp or persistent lower back pain, stop training and see a doctor.",
        "metadata": {"category": "safety", "topic": "lower_back_pain"},
    },
    {
        "id": "saf_003",
        "text": "Shoulder pain during pressing movements may indicate rotator cuff irritation. "
                "Avoid behind-the-neck presses. Strengthen the rotator cuff with band external rotations. "
                "Reduce pressing volume and add more pulling (rows, face pulls). "
                "Persistent shoulder pain requires physiotherapy assessment.",
        "metadata": {"category": "safety", "topic": "shoulder_pain"},
    },
    {
        "id": "saf_004",
        "text": "Overtraining syndrome occurs when training volume exceeds recovery capacity over time. "
                "Symptoms: persistent fatigue, declining performance, mood disturbances, frequent illness. "
                "Treatment: reduce training volume by 40–50% for 1–2 weeks (deload). "
                "Prevention: programme deload weeks every 4–6 weeks of training.",
        "metadata": {"category": "safety", "topic": "overtraining"},
    },

    # ── GOALS & MOTIVATION ────────────────────────────────────────────────────
    {
        "id": "mot_001",
        "text": "Consistency beats intensity for long-term fitness results. "
                "Three moderate workouts per week done consistently for a year "
                "will produce far greater results than intense sporadic training. "
                "Build habits first, then optimise intensity.",
        "metadata": {"category": "motivation", "topic": "consistency"},
    },
    {
        "id": "mot_002",
        "text": "SMART goals for fitness: Specific (lose 5 kg), Measurable (track weekly weight), "
                "Achievable (0.5 kg/week), Relevant (improves health), Time-bound (12 weeks). "
                "Break large goals into 4-week milestones. Celebrate small wins to maintain motivation.",
        "metadata": {"category": "motivation", "topic": "goal_setting"},
    },
    {
        "id": "mot_003",
        "text": "Weight loss plateaus are normal after 4–8 weeks of dieting. "
                "The body adapts by reducing metabolic rate. Solutions: 1–2 week diet break at maintenance, "
                "increase cardio by 20 minutes per session, reduce calories by a further 100–150 kcal. "
                "Do not drop calories below 1200 kcal (women) or 1500 kcal (men).",
        "metadata": {"category": "motivation", "topic": "plateau"},
    },
]
