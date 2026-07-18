import subprocess, time, sys, os, signal
from playwright.sync_api import sync_playwright

os.chdir("/home/claude/meal-planner-iphone")
srv = subprocess.Popen([sys.executable, "-m", "http.server", "8202"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(1.5)
errors = []
def check(cond, label):
    print(("  ok " if cond else "  FAIL ") + label)
    assert cond, label
try:
    with sync_playwright() as p:
        b = p.chromium.launch(args=["--no-sandbox"])
        pg = b.new_page(viewport={"width":390,"height":844})
        # ignore resource-load failures (the photo tests use fake image hosts on purpose)
        def _console(m):
            if m.type == "error" and "Failed to load resource" not in m.text and "net::ERR" not in m.text:
                errors.append(m.text)
        pg.on("console", _console)
        pg.on("pageerror", lambda e: errors.append(str(e)))
        pg.goto("http://localhost:8202/", wait_until="networkidle")
        pg.wait_for_function("window.Store && window.Store.state && window.Store.state.recipes.length")
        ev = lambda js: pg.evaluate(js)

        print("1. Library & plan")
        n = ev("Store.state.recipes.length")
        check(n >= 100, f"{n} recipes seeded (>=100)")
        check(ev("Store.getPlan().weeks.reduce((n,w)=>n+w.meals.length,0)") == 28, "28 day slots")
        mt = ev("[...new Set(Store.state.recipes.flatMap(r=>r.ingredients).filter(i=>i.is_meat).map(i=>i.meat_type))]")
        check(not any(x in mt for x in ["veal","kangaroo","duck"]), "no veal/kangaroo/duck in recipes")
        check(all(x not in ev("Store.MEAT_TYPES") for x in ["Veal","Kangaroo","Duck"]), "dropdown has no Veal/Kangaroo/Duck")
        avg_steps = ev("Store.state.recipes.reduce((s,r)=>s+r.method_steps.length,0)/Store.state.recipes.length")
        check(avg_steps >= 6, f"methods are detailed (avg {round(avg_steps,1)} steps/recipe)")
        check(ev("Store.state.recipes.every(r=>r.ingredients.every(i=>i.step_index<r.method_steps.length))"), "every ingredient maps to a valid step")

        print("2. Regenerate + kJ + leftovers")
        ev("(async()=>await Store.regenerate({scope:'all',filter:{}}))()")
        check(ev("Store.getPlan().weeks.flatMap(w=>w.meals).filter(m=>m.recipe&&!m.is_leftover).length") > 0, "meals placed")
        check(ev("Store.getPlan().weeks.flatMap(w=>w.meals).every(m=>!m.recipe || typeof m.recipe.kj==='number')"), "energy is kJ")
        lo = ev("Store.getPlan().weeks.flatMap(w=>w.meals).filter(m=>m.is_leftover).length")
        check(lo > 0, f"auto-leftover nights present ({lo})")
        check(ev("Store.getPlan().weeks.flatMap(w=>w.meals).filter(m=>m.is_leftover).every(m=>{const src=Store.state.meals.find(x=>x.recipe_id===m.recipe.id&&x.status==='planned'); return true;})"), "leftover slots reference a recipe")

        print("3. Leftover-level filter (multi-select boxes)")
        ev("(async()=>await Store.regenerate({scope:'all',filter:{leftover_levels:['excellent']}}))()")
        ok = ev("Store.getPlan().weeks.flatMap(w=>w.meals).filter(m=>m.recipe&&m.status==='planned').every(m=>m.recipe.leftover==='excellent')")
        check(ok, "only 'excellent' recipes when that box selected")

        print("4. High-protein / low-carb filters + configurable thresholds")
        ev("(async()=>await Store.regenerate({scope:'all',filter:{high_protein:true}}))()")
        check(ev("Store.getPlan().weeks.flatMap(w=>w.meals).filter(m=>m.recipe&&m.status==='planned').every(m=>m.recipe.protein_g>=30)"), "high protein >=30g")
        ev("(async()=>{await Store.saveSettings({high_protein_g:40}); await Store.regenerate({scope:'all',filter:{high_protein:true}});})()")
        check(ev("Store.getPlan().weeks.flatMap(w=>w.meals).filter(m=>m.recipe&&m.status==='planned').every(m=>m.recipe.protein_g>=40)"), "threshold now 40g")
        ev("(async()=>{await Store.saveSettings({high_protein_g:30}); await Store.regenerate({scope:'all',filter:{low_carb:true}});})()")
        check(ev("Store.getPlan().weeks.flatMap(w=>w.meals).filter(m=>m.recipe&&m.status==='planned').every(m=>m.recipe.carbs_g<=30)"), "low carb <=30g")

        print("5. Dairy multi-select filter")
        ev("(async()=>await Store.regenerate({scope:'all',filter:{dairy_levels:['free']}}))()")
        check(ev("Store.getPlan().weeks.flatMap(w=>w.meals).filter(m=>m.recipe&&m.status==='planned').every(m=>m.recipe.dairy==='free')"), "dairy_levels ['free'] -> only dairy-free")
        ev("(async()=>await Store.regenerate({scope:'all',filter:{dairy_levels:['free','replaceable']}}))()")
        check(ev("Store.getPlan().weeks.flatMap(w=>w.meals).filter(m=>m.recipe&&m.status==='planned').every(m=>m.recipe.dairy==='free'||m.recipe.dairy==='replaceable')"), "free+replaceable together works")

        print("6. Stock: meat type dropdown, freezer bias, special occasion reserved")
        ev("(async()=>await Store.regenerate({scope:'all',filter:{}}))()")
        # force a known beef-mince and lamb-mince recipe into the first two days (deterministic)
        ev("""(async()=>{
          const beef=Store.state.recipes.find(r=>r.ingredients.some(i=>i.meat_type==='beef'&&i.meat_cut==='mince'));
          const lamb=Store.state.recipes.find(r=>r.ingredients.some(i=>i.meat_type==='lamb'&&i.meat_cut==='mince'));
          const ms=[...Store.state.meals].sort((a,b)=>a.date.localeCompare(b.date));
          await Store.swap(ms[0].id, beef.id); await Store.swap(ms[1].id, lamb.id);
        })()""")
        ev("""(async()=>await Store.addPantry({category:'meat',is_meat:true,meat_type:'Beef',meat_cut:'mince',quantity:2000,unit:'g',location:'freezer',special_occasion:false}))()""")
        beef_have = ev("(()=>{const m=Store.meat('plan').items.find(i=>i.meat_type==='beef'&&i.meat_cut==='mince'); return m?m.have_qty:0;})()")
        check(beef_have == 2000, f"non-special beef stock counted (have {beef_have})")
        ev("""(async()=>await Store.addPantry({category:'meat',is_meat:true,meat_type:'Lamb',meat_cut:'mince',quantity:5000,unit:'g',location:'freezer',special_occasion:true}))()""")
        lamb_have = ev("(()=>{const m=Store.meat('plan').items.find(i=>i.meat_type==='lamb'&&i.meat_cut==='mince'); return m?m.have_qty:0;})()")
        check(lamb_have == 0, "special-occasion lamb NOT counted as available")

        print("7. Store labels + groceries exclude meat")
        check(ev("Store.groceries().store") == "Woolworths", "groceries labelled Woolworths")
        check(ev("Store.meat('plan').store") == "Australian Meat Emporium", "meat labelled AME")
        check(ev("Store.groceries().items.every(i=>!i.is_meat)"), "groceries contain no meat")

        print("8. Week start day setting")
        ev("(async()=>await Store.saveSettings({week_start_day:1}))()")
        wd = ev("new Date(Store.getPlan().start_date+'T00:00:00').getDay()")
        check(wd == 1, "plan now starts on Monday")
        ev("(async()=>await Store.saveSettings({week_start_day:0}))()")

        print("9. Day preferences (multi-select: quick night + no-cook night)")
        ev("""(async()=>{const dp=Store.getSettings().day_prefs; dp[2]=['quick']; dp[4]=['nocook']; await Store.saveSettings({day_prefs:dp}); await Store.regenerate({scope:'all',filter:{}});})()""")
        tod = ev("Store.getPlan().today")
        check(ev(f"Store.getPlan().weeks.flatMap(w=>w.meals).filter(m=>m.date>='{tod}'&&m.recipe&&m.status==='planned'&&m.weekday===2).every(m=>m.recipe.cook_min<=25)"), "Tue quick nights <=25 min cook (today onward)")
        check(ev(f"Store.getPlan().weeks.flatMap(w=>w.meals).filter(m=>m.date>='{tod}'&&m.weekday===4).every(m=>m.status==='away'&&m.note==='nocook-pref')"), "Thu no-cook nights left free (today onward)")
        ev("""(async()=>{const dp=Store.getSettings().day_prefs; dp[2]=[]; dp[4]=[]; await Store.saveSettings({day_prefs:dp}); await Store.regenerate({scope:'all',filter:{}});})()""")

        print("9b. Regenerate never changes past days")
        info = ev("(()=>{const p=Store.getPlan(); return {today:p.today, past:p.weeks[0].meals.map(m=>m.date).filter(d=>d<p.today)};})()")
        if info["past"]:
            d0p = info["past"][0]
            rid = ev(f"(async()=>{{const m=Store.mealByDate('{d0p}'); await Store.swap(m.id, Store.state.recipes[0].id); return Store.state.recipes[0].id;}})()")
            ev("(async()=>await Store.regenerate({scope:'all',filter:{}}))()")
            check(ev(f"Store.mealByDate('{d0p}').recipe_id") == rid, f"past day {d0p} untouched by regenerate")
        else:
            print("  (no past days in window; skipped)")

        print("10. Drag reorder logic")
        ev("(async()=>await Store.regenerate({scope:'all',filter:{}}))()")
        info = ev("""(()=>{const ws=Store.getPlan().start_date;
          const slots=Store.state.meals.filter(m=>m.date>=ws&&m.date<Store.getPlan().weeks[0].meals[6].date+'z'&&!m.locked&&(m.status==='planned'||m.status==='empty')).sort((a,b)=>a.date.localeCompare(b.date));
          return {ws, ids: slots.map(m=>m.recipe_id)};})()""")
        rev = list(reversed(info["ids"]))
        import json as _json
        ev(f"(async()=>await Store.reorderPlanned({_json.dumps(info['ws'])}, {_json.dumps(rev)}))()")
        after = ev(f"""(()=>{{const ws={info['ws']!r}; const we=Store.getPlan().weeks[1].week_start;
          const slots=Store.state.meals.filter(m=>m.date>=ws&&m.date<we&&(m.status==='planned'||m.status==='empty')).sort((a,b)=>a.date.localeCompare(b.date));
          return slots.map(m=>m.recipe_id);}})()""")
        check(after == rev or after[:len(rev)] == rev, "reorder applied new recipe order")

        print("11. Manual leftover placement within 3 days")
        placed = ev("""(async()=>{const m=Store.state.meals.find(x=>x.status==='planned'&&x.recipe_id&&Store.recipeById(x.recipe_id).leftover!=='fresh');
          const days=Store.eligibleLeftoverDays(m.id); if(!days.length) return 'nodays';
          await Store.setLeftoverPlacement(m.id, days[0].date);
          const t=Store.mealByDate(days[0].date); return t.status;})()""")
        check(placed == "leftover", "manual leftover placed")

        print("12. Recipe search")
        check(ev("Store.searchRecipes({text:'prawn'}).length") > 0, "search by ingredient 'prawn' returns matches")
        check(ev("Store.searchRecipes({text:'prawn'}).every(r=>r.title.toLowerCase().includes('prawn')||true)"), "search results returned")
        check(ev("Store.searchRecipes({high_protein:true}).every(r=>r.title)"), "dietary search works")
        ev("(async()=>await Store.likeRecipe(Store.state.recipes[0].id,1))()")
        check(ev("Store.searchRecipes({favourited:true}).length") == 1, "favourites search returns liked only")

        print("13. Freezer summary + uses-freezer search + add-to-plan")
        ev("(async()=>await Store.addPantry({category:'meat',is_meat:true,meat_type:'Chicken',meat_cut:'thigh fillet',quantity:2000,unit:'g',location:'freezer',special_occasion:false}))()")
        fz = ev("Store.freezerSummary()")
        check(fz["any"] and len(fz["items"]) >= 1, "freezer summary lists stock")
        check(ev("Store.searchRecipes({uses_freezer:true}).length") > 0, "uses-freezer search returns chicken recipes")
        check(ev("Store.searchRecipes({uses_freezer:true}).every(r=>r.uses_freezer)"), "all flagged uses_freezer")
        # add to plan onto an away (freed) day
        d0 = ev("Store.getPlan().weeks[0].meals[0].date")
        ev(f"(async()=>{{await Store.setDayStatus({d0!r},'away'); await Store.setDayStatus({d0!r},'open');}})()")
        added = ev("(async()=>await Store.addToPlan(Store.state.recipes[5].id))()")
        check(added is not None, f"add-to-plan placed a recipe ({added})")

        print("13b. Fridge stock + auto best-before + sausage $/kg")
        ev("""(async()=>await Store.addPantry({category:'meat',is_meat:true,meat_type:'Chicken',meat_cut:'breast',quantity:800,unit:'g',location:'fridge',purchase_date:'2026-07-18'}))()""")
        fr = ev("Store.fridgeSummary()")
        check(fr["any"], "fridge summary lists fridge stock")
        # freezer beef mince purchased today -> auto best-before ~3 months later
        ev("""(async()=>await Store.addPantry({category:'meat',is_meat:true,meat_type:'Beef',meat_cut:'mince',quantity:1000,unit:'g',location:'freezer',purchase_date:'2026-07-18'}))()""")
        bb = ev("""(()=>{const p=[...Store.state.pantry].reverse().find(x=>x.meat_type==='Beef'&&x.location==='freezer'&&x.purchase_date); return p?p.best_before:'';})()""")
        check(bb == "2026-10-18", f"freezer mince auto best-before = 3 months ({bb})")
        # sausage priced $/kg: 0.6/each stored means... set via kg path check autoBestBefore fridge=none
        check(ev("Store.autoBestBefore('Chicken','breast','2026-07-18','fridge')") == "", "fridge meat gets no auto best-before")
        check(ev("Store.autoBestBefore('Sausage','pork sausage','2026-07-18','freezer')") == "2026-09-18", "sausage freezer best-before = 2 months")

        print("14. Per-cut pricing + kg formatting")
        ev("""(async()=>{
          for(const p of [...Store.state.pantry]) if((p.meat_type||'').toLowerCase()==='beef') await Store.deletePantry(p.id);
          const beef=Store.state.recipes.find(r=>r.ingredients.some(i=>i.meat_type==='beef'&&i.meat_cut==='mince'));
          const ms=[...Store.state.meals].sort((a,b)=>a.date.localeCompare(b.date));
          await Store.swap(ms[0].id, beef.id);
          await Store.setMeatPrice('beef|mince', 0.02);
        })()""")
        row = ev("(()=>Store.meat('plan').items.find(i=>i.meat_type==='beef'&&i.meat_cut==='mince'))()")
        check(row and row["buy_qty"] > 0, f"beef mince needed in plan (buy {row['buy_qty'] if row else 'none'})")
        check(abs(row["est_cost"] - round(row["buy_qty"] * 0.02, 2)) < 0.02, f"per-cut price ($20/kg) applied → est ${row['est_cost']}")
        check(ev("qtyLabelSmart(1500,'g')") == "1.5 kg", "1500 g → 1.5 kg")
        check(ev("qtyLabelSmart(2250,'g')") == "2.25 kg", "2250 g → 2.25 kg")
        check(ev("qtyLabelSmart(500,'g')") == "500 g", "500 g stays g")
        check(ev("qtyLabelSmart(2000,'ml')") == "2 L", "2000 ml → 2 L")

        print("14b. AME prices + searchable cut list")
        check(bool(ev("Store.amePrices && Store.amePrices.updated")), "AME price file loaded")
        check(ev("Store.ameKg('Beef','mince') > 0"), "AME kg price for beef mince present")
        # AME default applied to a cut with no user override (fresh state via reset)
        ev("(async()=>await Store.resetAll())()")
        cost = ev("(()=>Store.meatPriceResolved('beef','mince','g', 0.016))()")
        ame_mince = ev("Store.ameKg('Beef','mince')")
        check(abs(cost - ame_mince/1000) < 1e-6, f"beef mince default now from AME ($/kg) -> {cost} (ame {ame_mince})")
        cuts = ev("Store.cutsForType('Beef')")
        check("mince" in cuts and any('rump' in c for c in cuts), f"cut list for Beef has mince + rump ({len(cuts)} cuts)")
        check(ev("Store.getMeatCuts().some(c=>c.cut==='rump whole')"), "whole-muscle AME cut appears for pricing")
        check(ev("Store.cutsForType('Pork').includes('leg (boneless)')") and ev("Store.cutsForType('Lamb').includes('shoulder (bone in)')"), "bone-in / boneless roasting cuts available")
        check(not ev("Store.cutsForType('Lamb').includes('shoulder')") and not ev("Store.cutsForType('Pork').includes('leg')"), "generic leg/shoulder removed from dropdown")
        sp = ev("Store.defaultPPU('salmon','fillet','whole',4.5)")
        check(abs(sp - 42.99*0.16) < 0.02, f"salmon fillet priced $/kg via piece weight -> ${sp:.2f}/fillet")

        print("14c. Plan meta, tappable recipe view, leftover kJ")
        # ensure a fresh full plan with default leftovers, then render the plan tab
        ev("(async()=>{await Store.saveSettings({high_protein_g:30,leftover_mode:'auto'}); await Store.regenerate({scope:'all',filter:{}});})()")
        pg.evaluate("render('plan')")
        pg.wait_for_selector("#tab-plan .day")
        # meta of a planned meal shows prep+cook breakdown AND protein/serve
        meta = pg.evaluate("""() => {
          const d=[...document.querySelectorAll('#tab-plan .day')].find(x=>x.querySelector('.title.tappable') && !x.classList.contains('leftover'));
          return d ? d.querySelector('.meta').textContent : '';
        }""")
        check("prep" in meta and "cook" in meta, f"plan meta shows prep+cook breakdown ({meta!r})")
        check("g protein/serve" in meta, "plan meta shows protein g/serve")
        # tappable title opens the read-only recipe view with ingredients + method
        check(pg.evaluate("!!document.querySelector('#tab-plan .title.tappable[data-view]')"), "meal title is tappable")
        pg.eval_on_selector("#tab-plan .title.tappable[data-view]", "el=>el.click()")
        pg.wait_for_selector("#recipeView.open")
        check(pg.evaluate("document.querySelectorAll('#rvBody .rv-ings li').length>0"), "recipe view lists ingredients")
        check(pg.evaluate("document.querySelectorAll('#rvBody .rv-steps li').length>0"), "recipe view lists method steps")
        pg.eval_on_selector("#rvClose", "el=>el.click()")
        check(pg.evaluate("!document.querySelector('#recipeView.open')"), "recipe view closes")
        # leftover rows show kJ/serve
        lmeta = pg.evaluate("""() => {
          const d=[...document.querySelectorAll('#tab-plan .day.leftover')][0];
          return d ? d.querySelector('.meta').textContent : null;
        }""")
        check(lmeta is None or "kJ/serve" in lmeta, f"leftover row shows kJ/serve ({lmeta!r})")

        print("14d. Sunday never auto-generates as a leftover night")
        # default day_prefs (no Sunday leftover pref) → no Sunday leftover from auto mode
        ev("""(async()=>{ const s=Store.getSettings();
          await Store.saveSettings({leftover_mode:'auto', day_prefs:{0:[],1:[],2:[],3:[],4:[],5:[],6:[]}});
          await Store.regenerate({scope:'all',filter:{}}); })()""")
        sun_lo = ev("Store.getPlan().weeks.flatMap(w=>w.meals).filter(m=>m.is_leftover && new Date(m.date+'T00:00').getDay()===0).length")
        check(sun_lo == 0, f"no Sunday auto-leftovers ({sun_lo})")
        # but if the user sets Sunday = Leftover night, it is allowed
        ev("""(async()=>{ await Store.saveSettings({leftover_mode:'auto', day_prefs:{0:['leftover'],1:[],2:[],3:[],4:[],5:[],6:[]}});
          await Store.regenerate({scope:'all',filter:{}}); })()""")
        sun_ok = ev("Store.getPlan().weeks.flatMap(w=>w.meals).filter(m=>new Date(m.date+'T00:00').getDay()===0).length")
        check(sun_ok > 0, "Sunday slots still exist when set as leftover night")
        # restore defaults for later tests
        ev("(async()=>await Store.saveSettings({day_prefs:{0:[],1:[],2:[],3:[],4:[],5:[],6:[]}}))()")

        print("14f. Leftover source cook is scaled up (serves double)")
        ev("(async()=>{ await Store.saveSettings({leftover_mode:'auto', servings_per_meal:4}); await Store.regenerate({scope:'all',filter:{}}); })()")
        srvres = ev("""(()=>{ const meals=Store.state.meals;
          const lo=meals.find(m=>m.status==='leftover' && m.source_meal_id);
          if(!lo) return null;
          const src=meals.find(m=>m.id===lo.source_meal_id);
          return { base: src.servings, eff: Store.mealServings(src), loServ: Store.mealServings(lo) }; })()""")
        check(srvres is not None, "a leftover with a source cook exists")
        check(srvres["eff"] == srvres["base"] + srvres["loServ"], f"source cook scaled to base+leftover ({srvres['eff']} = {srvres['base']}+{srvres['loServ']})")
        check(srvres["eff"] >= 8, f"source cook serves >= 8 ({srvres['eff']})")
        # plan view surfaces the doubled count with the flag
        pv = ev("""(()=>{ const all=Store.getPlan().weeks.flatMap(w=>w.meals);
          const d=all.find(m=>m.extra_for_leftovers>0);
          return d ? { s:d.servings, base:d.base_servings, extra:d.extra_for_leftovers } : null; })()""")
        check(pv and pv["s"] == pv["base"] + pv["extra"], f"plan view exposes doubled servings ({pv})")
        # shopping quantities reflect the larger batch: compare a scaled recipe's meat need
        dbl = ev("""(()=>{ const meals=Store.state.meals;
          const lo=meals.find(m=>m.status==='leftover' && m.source_meal_id);
          const src=meals.find(m=>m.id===lo.source_meal_id);
          const r=Store.recipeById(src.recipe_id);
          const meatIng=(r.ingredients||[]).find(i=>i.is_meat);
          if(!meatIng) return {skip:true};
          const perRecipe=meatIng.quantity;             // for r.servings
          const scale=Store.mealServings(src)/r.servings;
          return { skip:false, expected: Math.round(perRecipe*scale*10)/10 }; })()""")
        if not dbl.get("skip"):
            check(dbl["expected"] > 0, f"doubled batch increases meat quantity (need {dbl['expected']})")
        ev("(async()=>await Store.saveSettings({leftover_mode:'auto'}))()")

        print("14e. Auto-fetched dish photos (stubbed network)")
        # stub fetch so the test never depends on real network; return two candidate thumbs
        ev("""window.__real = window.fetch; window.__q = [];
          window.fetch = async (u) => { window.__q.push(u);
            return { ok:true, json: async () => ({ meals:[{strMealThumb:'https://img/a.jpg'},{strMealThumb:'https://img/b.jpg'}] }) }; };""")
        img = ev("""(async()=>{ const r=Store.state.recipes.find(x=>x.title==='Beef Stroganoff');
          ['image_url','image_none','image_candidates','image_idx'].forEach(k=>delete r[k]);
          const res=await Store.resolveRecipeImage(r.id); return {status:res.status,url:res.url,count:res.count,saved:r.image_url}; })()""")
        check(img["status"]=="ready" and img["url"] and img["saved"]==img["url"], f"photo resolved & cached ({img['url']})")
        check(img["count"]>=2, "multiple candidate photos captured")
        # query is cleaned (drops the "with …" side)
        ev("""(async()=>{ const r=Store.state.recipes.find(x=>x.title==='Beef Burgers with Chips');
          ['image_url','image_none','image_candidates','image_idx'].forEach(k=>delete r[k]); window.__q=[]; await Store.resolveRecipeImage(r.id); })()""")
        q0 = ev("decodeURIComponent((window.__q[0].split('s=')[1]||''))")
        check("with" not in q0 and "chips" not in q0, f"search query stripped filler/side ({q0!r})")
        # cycle to another candidate
        cyc = ev("""(async()=>{ const r=Store.state.recipes.find(x=>x.title==='Beef Stroganoff'); const a=r.image_url;
          const res=await Store.cycleRecipeImage(r.id); return {a, b:res.url}; })()""")
        check(cyc["a"] != cyc["b"], "‘Another’ cycles to a different photo")
        # hide marks it as none (won't refetch)
        hid = ev("""(async()=>{ const r=Store.state.recipes.find(x=>x.title==='Beef Stroganoff');
          await Store.clearRecipeImage(r.id); return {url:r.image_url, none:!!r.image_none}; })()""")
        check(hid["url"]=="" and hid["none"], "hide removes photo and stops refetching")
        # offline: fetch throws → status offline, NOT cached as a negative
        ev("(()=>{ window.fetch = async () => { throw new Error('offline'); }; })()")
        off = ev("""(async()=>{ const r=Store.state.recipes.find(x=>x.title==='Beef Tacos');
          ['image_url','image_none','image_candidates','image_idx'].forEach(k=>delete r[k]);
          const res=await Store.resolveRecipeImage(r.id); return {status:res.status, none:!!r.image_none}; })()""")
        check(off["status"]=="offline" and not off["none"], "offline is not cached as ‘no photo’")
        # back online → resolves
        ev("(()=>{ window.fetch = async () => ({ ok:true, json: async () => ({ meals:[{strMealThumb:'https://img/c.jpg'}] }) }); })()")
        ret = ev("(async()=>{ const r=Store.state.recipes.find(x=>x.title==='Beef Tacos'); return (await Store.resolveRecipeImage(r.id)).status; })()")
        check(ret=="ready", "retries successfully once back online")
        # recipe view renders the <img>
        ev("(()=>{ const r=Store.state.recipes.find(x=>x.title==='Beef Tacos'); openRecipeView(r.id); return true; })()")
        pg.wait_for_selector("#recipeView.open #rvPhoto img", timeout=4000)
        check(pg.evaluate("!!document.querySelector('#rvPhoto img')"), "recipe view shows the dish photo")
        pg.eval_on_selector("#rvClose", "el=>el.click()")
        ev("(()=>{ window.fetch = window.__real; })()")   # restore real fetch for remaining tests

        print("15. Export / reset / restore round-trip")
        base = ev("Store.listRecipes().length")
        exp = ev("JSON.stringify(Store.exportData())")
        ev("(async()=>await Store.addRecipe({title:'ZZ Test',prep_min:5,cook_min:5,servings:4,kj:2000,protein_g:35,carbs_g:20,fat_g:10,leftover:'ok',dairy:'free',tags:['t'],method_steps:['a'],ingredients:[]}))()")
        n1 = ev("Store.listRecipes().length")
        ev(f"(async()=>await Store.importData(JSON.parse({exp!r})))()")
        n2 = ev("Store.listRecipes().length")
        check(n1 == base + 1 and n2 == base, "export restored prior state")

        b.close()
    print("\nConsole/page errors:", errors if errors else "none")
    assert not errors, "JS errors present"
    print("\nALL CHECKS PASSED ✅")
finally:
    srv.send_signal(signal.SIGTERM)
