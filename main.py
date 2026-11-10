import io_manager
import ai_manager
import data_manager
import logic_manager
import json

def main():
	io = io_manager.IOManager()
	ai = ai_manager.AiManager()
	data = data_manager.DataManager()

	# Update database to remove closed reports that have been closed for more than 30 days
	print("=" * 20)
	print("Updating database")
	print("=" * 20)
	deleted = data.delete_expired_reports(30)  # Delete reports closed for more than 30 days
	print(f"[+] Database updated. {deleted} closed reports deleted from the database.")
	
	active_logic = None
	
	while True:
		# Clear items in the temporary directory to avoid clutter and potential conflicts
		data.clear_temp_directory()

		# Run the CLI interface for the AI powered lost and found system
		while True:
			user_report, configured_logic = io.run_cli(current_logic=active_logic)

			# Update persistent logic instance if user configured it
			if configured_logic is not None:
				active_logic = configured_logic
			
			# If a report was submitted, break to process it
			if user_report is not None and user_report != "quit":
				# If logic was never configured by user, fallback to default
				if active_logic is None:
					active_logic = logic_manager.LogicManager()

				logic = active_logic
				break

			if user_report == "quit":
				break
		
		if user_report == "quit":
			break

		# AI layer to process report types
		elif type(user_report) == dict:
			print(f"\n[+] {user_report.get("report_type")} report received. Sending to AI layer for processing...")
			# AI powered feature extraction
			if user_report.get("image_path") is not None:
				extract_image_path = data.store_image(user_report.get("image_path"), None)

			else:
				extract_image_path = None
			user_input_extracted = ai.extract_features(user_report, extract_image_path)

			if user_input_extracted is None:
				continue

			user_input_extracted = json.loads(user_input_extracted)
			# Found reports workflow: Extract features and store into database
			if user_report.get("report_type") == "found":
				# Store report into database
				print("[+] Storing found report into database...")
				try:
					data.save_new_reports(user_input_extracted)
				except Exception as e:
					print(f"[!] Error saving report: {e}")
					continue

				print("\n" + "=" * 50)
				print("Found report stored successfully into database!")
				print("=" * 50)
			
			# Lost reports workflow: Extract features, perform semantic matching, pass to logic manager and output to user
			elif user_report.get("report_type") == "lost":
				# AI powered semantic matching
				print("\n" + "=" * 70)
				print("Attempting AI semantic matching with found reports in the database")
				print("=" * 70)
				print("[+] Pulling found reports from database for AI semantic matching...")
	
				# Pull found records from same category as the lost report from database
				report_category_list = data.get_reports_by_category(user_input_extracted.get("category"))
				if not report_category_list:
					print(f"[!] No found reports reported for category: {user_input_extracted.get('category')}.")
					continue
				print(f"[+] Found {len(report_category_list)} found reports for category: {user_input_extracted.get('category')}.")
				matching_lost_reports = ai.ai_semantic_matching(user_input_extracted, report_category_list) 

				if not matching_lost_reports:
					continue

				# Business logic layer to apply multi rule conditions and output the best match to the user
				print("\n" + "=" * 75)
				print("Applying business logic to determine the best match for the lost report")
				print("=" * 75)
				matching_results = json.loads(matching_lost_reports)
				best_match = logic.get_best_match(matching_results, user_input_extracted.get("date"))

				if best_match is None:
					print("[!] No suitable match found for the lost report found in the database.")
					continue

				# Mark report as closed in the database if user confirms that the match is correct
				resolve_report = io.resolve_best_match(best_match, alternative_matches=matching_results)
				if resolve_report:
					print("\n" + "=" * 75)
					print("Report marked as closed. Closing the matched found report in the databases")
					print("=" * 75)
					report = best_match.get("report")
					caseid = report.get("case_id")
					update_status = data.update_report_status(caseid, "closed")
					if update_status:
						print(f"[+] Report with case ID: {caseid} has been successfully closed.")
					else:
						print(f"[!] Failed to close report with case ID: {caseid}")

	return

if __name__=="__main__":
	main()
