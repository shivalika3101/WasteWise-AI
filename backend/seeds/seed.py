from app.database import get_session_factory
from app.models import (
    Bin,
    BlogPost,
    Category,
    CategoryBin,
    DisposalInstruction,
)

from seeds.seed_data import (
    BINS,
    BLOG_POSTS,
    CATEGORIES,
    CATEGORY_BINS,
    DISPOSAL_INSTRUCTIONS,
)

Session = get_session_factory()


# =====================================================
# Seed Bins
# =====================================================

def seed_bins(session):
    print("Seeding bins...")

    for data in BINS:
        existing = (
            session.query(Bin)
            .filter_by(name=data["name"])
            .first()
        )

        if existing:
            existing.colour = data["colour"]
            existing.description = data["description"]
        else:
            session.add(
                Bin(
                    name=data["name"],
                    colour=data["colour"],
                    description=data["description"],
                )
            )

    session.commit()
    print("✓ Bins seeded.")


# =====================================================
# Seed Categories
# =====================================================

def seed_categories(session):
    print("Seeding categories...")

    for data in CATEGORIES:
        existing = (
            session.query(Category)
            .filter_by(name=data["name"])
            .first()
        )

        if existing:
            existing.display_name = data["display_name"]
            existing.model_label_index = data["model_label_index"]
        else:
            session.add(
                Category(
                    name=data["name"],
                    display_name=data["display_name"],
                    model_label_index=data["model_label_index"],
                )
            )

    session.commit()
    print("✓ Categories seeded.")


# =====================================================
# Seed Category -> Bin Mapping
# =====================================================

def seed_category_bins(session):
    print("Seeding category-bin mappings...")

    for category_name, bin_name in CATEGORY_BINS:

        category = (
            session.query(Category)
            .filter_by(name=category_name)
            .first()
        )

        if category is None:
            raise RuntimeError(
                f"Category '{category_name}' does not exist."
            )

        bin_obj = (
            session.query(Bin)
            .filter_by(name=bin_name)
            .first()
        )

        if bin_obj is None:
            raise RuntimeError(
                f"Bin '{bin_name}' does not exist."
            )

        existing = (
            session.query(CategoryBin)
            .filter_by(
                category_id=category.id,
                bin_id=bin_obj.id,
            )
            .first()
        )

        if existing:
            existing.is_primary = True
        else:
            session.add(
                CategoryBin(
                    category_id=category.id,
                    bin_id=bin_obj.id,
                    is_primary=True,
                )
            )

    session.commit()
    print("✓ Category-bin mappings seeded.")


# =====================================================
# Seed Disposal Instructions
# =====================================================

def seed_disposal_instructions(session):
    print("Seeding disposal instructions...")

    for data in DISPOSAL_INSTRUCTIONS:

        category = (
            session.query(Category)
            .filter_by(name=data["category"])
            .first()
        )

        if category is None:
            raise RuntimeError(
                f"Category '{data['category']}' does not exist."
            )

        existing = (
            session.query(DisposalInstruction)
            .filter_by(category_id=category.id)
            .first()
        )

        if existing:
            existing.instructions = data["instructions"]
            existing.notes = data["notes"]
        else:
            session.add(
                DisposalInstruction(
                    category_id=category.id,
                    instructions=data["instructions"],
                    notes=data["notes"],
                )
            )

    session.commit()
    print("✓ Disposal instructions seeded.")

# =====================================================
# Seed Blog Posts
# =====================================================

def seed_blog_posts(session):
    print("Seeding blog posts...")

    for data in BLOG_POSTS:
        existing = (
            session.query(BlogPost)
            .filter_by(slug=data["slug"])
            .first()
        )

        if existing:
            existing.title = data["title"]
            existing.summary = data["summary"]
            existing.body = data["body"]
            existing.status = data["status"]
        else:
            session.add(
                BlogPost(
                    slug=data["slug"],
                    title=data["title"],
                    summary=data["summary"],
                    body=data["body"],
                    status=data["status"],
                )
            )

    session.commit()
    print("✓ Blog posts seeded.")


    # =====================================================
# Verify Counts
# =====================================================

def verify_counts(session):
    print("\nVerifying database counts...")

    category_count = session.query(Category).count()
    bin_count = session.query(Bin).count()
    mapping_count = session.query(CategoryBin).count()
    instruction_count = session.query(DisposalInstruction).count()
    blog_post_count = session.query(BlogPost).count()

    print(f"Categories            : {category_count}")
    print(f"Bins                  : {bin_count}")
    print(f"Category-Bin Mappings : {mapping_count}")
    print(f"Instructions          : {instruction_count}")
    print(f"Blog posts            : {blog_post_count}")

    assert category_count == len(CATEGORIES), (
        f"Expected {len(CATEGORIES)} categories, found {category_count}"
    )

    assert bin_count == len(BINS), (
        f"Expected {len(BINS)} bins, found {bin_count}"
    )

    assert mapping_count == len(CATEGORY_BINS), (
        f"Expected {len(CATEGORY_BINS)} mappings, found {mapping_count}"
    )

    assert instruction_count == len(DISPOSAL_INSTRUCTIONS), (
        f"Expected {len(DISPOSAL_INSTRUCTIONS)} instructions, found {instruction_count}"
    )

    assert blog_post_count == len(BLOG_POSTS), (
        f"Expected {len(BLOG_POSTS)} blog posts, found {blog_post_count}"
    )

    print("✓ Database counts verified.")


# =====================================================
# Verify Model Labels
# =====================================================

def verify_model_labels(session):
    print("\nVerifying model label indices...")

    indices = [
        category.model_label_index
        for category in session.query(Category)
        .order_by(Category.model_label_index)
        .all()
    ]

    expected = list(range(len(CATEGORIES)))

    if indices != expected:
        raise RuntimeError(
            f"Model label indices are incorrect.\n"
            f"Expected: {expected}\n"
            f"Found:    {indices}"
        )

    print("✓ Model labels verified.")


# =====================================================
# Verify Category Mappings
# =====================================================

def verify_category_mappings(session):
    print("\nVerifying category mappings...")

    categories = session.query(Category).all()

    for category in categories:

        mapping = (
            session.query(CategoryBin)
            .filter_by(category_id=category.id)
            .first()
        )

        if mapping is None:
            raise RuntimeError(
                f"Category '{category.name}' has no bin mapping."
            )

        instruction = (
            session.query(DisposalInstruction)
            .filter_by(category_id=category.id)
            .first()
        )

        if instruction is None:
            raise RuntimeError(
                f"Category '{category.name}' has no disposal instruction."
            )

    print("✓ Every category has a bin mapping and disposal guidance.")


# =====================================================
# Main
# =====================================================

def main():

    session = Session()

    try:
        print("=" * 60)
        print("WasteWise AI Database Seeder")
        print("=" * 60)

        seed_bins(session)
        seed_categories(session)
        seed_category_bins(session)
        seed_disposal_instructions(session)
        seed_blog_posts(session)

        verify_counts(session)
        verify_model_labels(session)
        verify_category_mappings(session)

        print("\n" + "=" * 60)
        print("Database seeded successfully.")
        print("=" * 60)

    except Exception as e:
        session.rollback()
        print("\nDatabase seeding failed.")
        raise e

    finally:
        session.close()


if __name__ == "__main__":
    main()